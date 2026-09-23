# Laboratorio de CI — Clasificador de solicitudes de "Trámites al Día"

**Módulo 4 · DevOps y CI/CD · Sesión 1** — Diplomado Automatización de Procesos con IA
Indra · UPTC · Tec de Monterrey · ProBoyacá

Todo el laboratorio se hace **desde el navegador, dentro de GitHub**. No hay que instalar Git, ni Python, ni nada.

---

## Qué vamos a construir

Esta es una API pequeña que resuelve un problema real de "Trámites al Día": el ciudadano escribe su solicitud en texto libre ("quiero pagar la multa", "necesito un certificado de residencia") y un modelo de IA la clasifica en una de cuatro categorías para enviarla a la cola correcta.

| Categoría | Ejemplo de solicitud |
|---|---|
| `renovacion` | "se me venció el permiso y lo quiero renovar" |
| `certificado` | "necesito una constancia de residencia" |
| `pago` | "no aparece reflejado el pago que hice ayer" |
| `queja` | "llevo tres semanas esperando respuesta" |

Sobre esa API vamos a construir el pipeline de integración continua en cuatro etapas:

| Etapa | Qué le agrega al pipeline |
|---|---|
| 1 | Correr las pruebas automáticamente en cada cambio |
| 2 | Revisar el estilo del código (lint) antes de gastar tiempo en pruebas |
| 3 | Probar en dos versiones de Python y exigir una cobertura mínima |
| 4 | **Quality gate del modelo**: frenar el cambio si la IA empeora |

---

## Qué hay en el repositorio

```
app/clasificador.py        el modelo (TF-IDF + regresión logística) y la limpieza del texto
app/main.py                la API: GET /health y POST /clasificar
data/entrenamiento.csv     48 solicitudes etiquetadas con las que se entrena el modelo
data/evaluacion.csv        16 solicitudes que el modelo NUNCA ve al entrenar; miden su exactitud
tests/test_clasificador.py pruebas unitarias
tests/test_api.py          pruebas de la API
tests/test_calidad_modelo.py  el quality gate: exige exactitud >= 80%
etapas/                    el workflow en sus 4 etapas, para ir copiando
.github/workflows/ci.yml   el pipeline final ya armado
```

---

## Paso 0 · Preparar tu copia (10 min)

1. **Fork.** Arriba a la derecha de esta página, pulsa **Fork** y luego **Create fork**. Eso te deja una copia del repositorio en tu propia cuenta, donde puedes romper lo que quieras.
2. **Habilitar Actions.** En *tu* fork, entra a la pestaña **Actions** y pulsa el botón **"I understand my workflows, go ahead and enable them"**.
   > GitHub desactiva los workflows en todos los forks hasta que el dueño los habilita. Si te saltas este paso, el pipeline nunca corre y no aparece ningún mensaje de error.
3. **Borrar el pipeline que ya viene.** Abre `.github/workflows/ci.yml`, pulsa el ícono de papelera (**Delete file**) y confirma con **Commit changes**. Lo vamos a reconstruir desde cero.

A partir de aquí, todo se hace en **tu fork**.

---

## Paso 1 · Tu primer pipeline (15 min)

1. En la página principal de tu fork: **Add file → Create new file**.
2. En el nombre escribe exactamente: `.github/workflows/ci.yml`
   > Al escribir cada `/`, GitHub va creando las carpetas solo.
3. Pega este contenido:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  pruebas:
    runs-on: ubuntu-latest
    steps:
      - name: Descargar el código
        uses: actions/checkout@v7

      - name: Instalar Python
        uses: actions/setup-python@v7
        with:
          python-version: "3.12"

      - name: Instalar dependencias
        run: pip install -r requirements-dev.txt

      - name: Correr las pruebas
        run: pytest -v
```

4. **Commit changes** (directo a `main`).
5. Ve a la pestaña **Actions**. En segundos aparece tu ejecución. Entra y abre cada paso para ver el log.

**Qué debe pasar:** todo en verde en menos de un minuto, y en el último paso, `10 passed`.

**Cómo leerlo:**

- `on:` son los disparadores. Este pipeline corre con cada push a `main` y con cada Pull Request hacia `main`.
- `runs-on: ubuntu-latest` le pide a GitHub una máquina Linux nueva. Nace vacía y se destruye al terminar: por eso el primer paso siempre es descargar el código.
- `uses:` invoca una acción ya publicada por otros. `run:` ejecuta un comando de consola.
- Si cualquier paso termina con error, el job se detiene y queda en rojo. Eso no hay que programarlo.

---

## Paso 2 · Lint y caché (15 min)

Abre `.github/workflows/ci.yml`, pulsa el lápiz (**Edit**), **reemplaza todo** el contenido por esto y haz commit:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  lint:
    name: Lint y formato
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: "3.12"
      - run: pip install ruff==0.15.11
      - name: Reglas de estilo y errores comunes
        run: ruff check .
      - name: Formato del código
        run: ruff format --check .

  pruebas:
    name: Pruebas
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: "3.12"
          cache: pip
          cache-dependency-path: requirements-dev.txt
      - run: pip install -r requirements-dev.txt
      - run: pytest -v
```

Dos cosas cambiaron:

- **`needs: lint`** — el job de pruebas espera al de lint. Si el lint falla, las pruebas ni arrancan.
- **`cache: pip`** — la segunda ejecución reutiliza los paquetes ya descargados. Compara el tiempo del paso "Instalar dependencias" entre esta ejecución y la siguiente.

### Rómpelo a propósito

Edita `app/main.py` y agrega en la segunda línea:

```python
import os
```

Haz commit y mira la pestaña Actions:

- **Lint y formato** falla en unos 15 segundos con `F401 'os' imported but unused`.
- **Pruebas** aparece como omitido: nunca llegó a correr.

Un import que sobra no rompe nada en ejecución, pero es basura que se acumula. El pipeline lo detecta antes de gastar un minuto de máquina en pruebas que igual no se iban a aceptar.

Quita la línea, haz commit y vuelve a verde.

---

## Paso 3 · Matriz de versiones y cobertura (12 min)

Reemplaza otra vez el contenido de `ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  lint:
    name: Lint y formato
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: "3.12"
      - run: pip install ruff==0.15.11
      - run: ruff check .
      - run: ruff format --check .

  pruebas:
    name: Pruebas (Python ${{ matrix.python-version }})
    needs: lint
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.12", "3.13"]
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
          cache-dependency-path: requirements-dev.txt
      - run: pip install -r requirements-dev.txt
      - name: Pruebas con cobertura (mínimo 80%)
        run: pytest -v --cov=app --cov-report=term-missing --cov-report=xml --cov-fail-under=80
      - name: Guardar el reporte de cobertura
        if: matrix.python-version == '3.12'
        uses: actions/upload-artifact@v7
        with:
          name: cobertura
          path: coverage.xml
```

**Qué debe pasar:** el job de pruebas se lanza dos veces en paralelo, una por cada versión de Python. Al final de la ejecución, abajo, aparece el artefacto **cobertura** para descargar.

- **`matrix`** repite el mismo job cambiando un valor. Así se detecta el código que funciona en una versión de Python y no en otra.
- **`--cov-fail-under=80`** convierte la cobertura en una regla: si las pruebas cubren menos del 80% del código, el job falla.
- Ojo: la cobertura mide qué líneas se ejecutaron durante las pruebas, **no** si las pruebas verifican algo útil. Un 100% con pruebas vacías no protege de nada.

---

## Paso 4 · El quality gate del modelo (15 min)

Este es el paso que diferencia un pipeline de software tradicional de uno para una solución con IA. Reemplaza el contenido de `ci.yml` por la versión final:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    name: Lint y formato
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: "3.12"
      - run: pip install ruff==0.15.11
      - run: ruff check .
      - run: ruff format --check .

  pruebas:
    name: Pruebas (Python ${{ matrix.python-version }})
    needs: lint
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.12", "3.13"]
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
          cache-dependency-path: requirements-dev.txt
      - run: pip install -r requirements-dev.txt
      - name: Pruebas unitarias y de API con cobertura (mínimo 80%)
        run: >
          pytest -v --ignore=tests/test_calidad_modelo.py
          --cov=app --cov-report=term-missing --cov-report=xml --cov-fail-under=80
      - name: Guardar el reporte de cobertura
        if: matrix.python-version == '3.12'
        uses: actions/upload-artifact@v7
        with:
          name: cobertura
          path: coverage.xml

  calidad-modelo:
    name: Quality gate del modelo
    needs: pruebas
    runs-on: ubuntu-latest
    env:
      UMBRAL_EXACTITUD: "0.80"
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: "3.12"
          cache: pip
          cache-dependency-path: requirements-dev.txt
      - run: pip install -r requirements-dev.txt
      - name: Exactitud del clasificador sobre datos de evaluación
        run: pytest -v -s tests/test_calidad_modelo.py
```

Abre `tests/test_calidad_modelo.py` y léelo: entrena el modelo, le pasa las 16 solicitudes de `data/evaluacion.csv` (que nunca vio al entrenar), calcula el porcentaje de aciertos y falla si baja del umbral.

**Qué debe pasar:** tres jobs en cadena, todos en verde, y en el resumen de la ejecución aparece *Exactitud del modelo: 100.00%*.

### Rómpelo a propósito

Imagina que un compañero quiere que el modelo ocupe menos memoria. Abre `app/clasificador.py` y cambia la línea del vectorizador por esta:

```python
            ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), max_features=10)),
```

Haz commit y observa:

- **Lint y formato:** verde. El código está perfectamente escrito.
- **Pruebas 3.12 y 3.13:** verde. La API responde, la cobertura sigue en 100%.
- **Quality gate del modelo:** rojo. *Exactitud 56.25% por debajo del umbral 80%*.

No se rompió el código: se rompió el comportamiento del modelo. Sin este job, el cambio habría llegado a producción y casi la mitad de las solicitudes de los ciudadanos habrían terminado en la cola equivocada. Esa es la diferencia entre CI para software y CI para soluciones con IA.

Devuelve la línea como estaba y vuelve a verde.

---

## Paso 5 · Proteger `main` con un Pull Request (18 min)

Hasta ahora has hecho commit directo a `main`. En un equipo real eso no se permite: los cambios entran por Pull Request y solo si el pipeline está en verde.

### 5.1 Crear la regla

1. **Settings → Rules → Rulesets → New ruleset → New branch ruleset**.
   > En algunas cuentas aparece como **Settings → Branches → Add branch protection rule**. Da lo mismo.
2. Nombre: `proteger main`. **Enforcement status: Active**.
3. En **Target branches → Add target → Include default branch**.
4. Marca **Require a pull request before merging**.
5. Marca **Require status checks to pass** y agrega los cuatro:
   `Lint y formato`, `Pruebas (Python 3.12)`, `Pruebas (Python 3.13)`, `Quality gate del modelo`.
   > GitHub solo deja buscar checks que ya corrieron alguna vez en el repositorio. Por eso esta configuración va de última.
6. **Create**.

### 5.2 Probar que la regla funciona

1. Abre `app/clasificador.py` y pulsa el lápiz.
2. Dentro de la función `normalizar`, borra estas dos líneas:

```python
    if not texto or not texto.strip():
        raise ValueError("El texto de la solicitud no puede estar vacío")
```

3. Abajo, en **Commit changes**, escoge **Create a new branch for this commit and start a pull request**. Nombre de la rama: `bug/validacion`. **Propose changes** y luego **Create pull request**.
4. El pipeline arranca solo. Dos pruebas fallan (`test_normalizar_rechaza_texto_vacio` y `test_clasificar_texto_vacio_da_422`) y el botón **Merge pull request** queda bloqueado.
5. En el mismo Pull Request, pestaña **Files changed**, vuelve a poner las dos líneas y haz commit en la rama `bug/validacion`.
6. El pipeline corre de nuevo, todo pasa a verde y el merge se habilita.

Ahí el pipeline dejó de ser un tablero informativo y se convirtió en una regla del equipo: nadie integra código en rojo, ni el líder técnico.

---

## Si algo se rompe

| Síntoma | Qué revisar |
|---|---|
| La pestaña Actions no muestra ninguna ejecución | Falta habilitar los workflows en el fork (Paso 0.2) |
| "Workflow file issue" o un error de YAML | La indentación. En YAML los espacios importan y no se pueden usar tabuladores |
| Todo falla en "Instalar dependencias" | Revisa que el nombre del archivo sea exactamente `.github/workflows/ci.yml` y que el paso de checkout esté presente |
| No aparecen los checks al configurar la regla | Deben haber corrido al menos una vez con ese nombre exacto |
| Quiero volver a correr una ejecución | Entra a la ejecución y pulsa **Re-run jobs** |

---

## Trabajo autónomo

1. Agrega cinco ejemplos nuevos por categoría a `data/entrenamiento.csv` y verifica que el quality gate siga en verde.
2. Sube el umbral a `0.90` (variable `UMBRAL_EXACTITUD` en el workflow) y comprueba si el modelo lo aguanta.
3. Agrega un job que construya la imagen Docker de la API con `docker build` (el `Dockerfile` ya está en el repositorio, aún sin publicarla). Ese es el punto de partida de la Sesión 2: entrega continua.

---

## Para correrlo en tu máquina (opcional, no hace falta hoy)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
ruff check . && ruff format --check .
pytest -v --cov=app
uvicorn app.main:app --reload     # http://127.0.0.1:8000/docs
```
