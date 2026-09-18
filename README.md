# Laboratorio CI — Clasificador de solicitudes de "Trámites al Día"

Módulo 4 · DevOps y CI/CD · Sesión 1
Diplomado Automatización de Procesos con IA (Indra · UPTC · Tec de Monterrey · ProBoyacá)

Una API pequeña en Python (FastAPI) que recibe el texto que escribe un ciudadano y lo clasifica en
`renovacion`, `certificado`, `pago` o `queja` con un modelo de scikit-learn. Sobre ella se construye,
paso a paso, un pipeline de integración continua en GitHub Actions.

## Qué necesitas

- Una cuenta de GitHub (gratuita). En repositorios públicos, GitHub Actions no tiene costo.
- Navegador. Todo el laboratorio se puede hacer desde la web de GitHub, sin instalar nada.
- Opcional: Git y Python 3.12 si prefieres trabajar en tu máquina.

## Estructura

```
app/clasificador.py        modelo (TF-IDF + regresión logística) y limpieza del texto
app/main.py                API: GET /health y POST /clasificar
data/entrenamiento.csv     datos con los que se entrena el modelo
data/evaluacion.csv        datos que el modelo nunca ve al entrenar; miden su exactitud
tests/                     pruebas unitarias, de API y quality gate del modelo
etapas/                    el workflow en sus 3 primeras etapas, para ir copiando
.github/workflows/ci.yml   versión final del pipeline (etapa 4)
```

## Pasos del laboratorio

### 0. Prepara tu copia (10 min)

1. Haz *fork* de este repositorio a tu cuenta.
2. Entra a la pestaña **Actions** de tu fork y pulsa **"I understand my workflows, go ahead and enable them"**.
   GitHub desactiva los workflows en los forks hasta que tú lo confirmes.
3. Borra el archivo `.github/workflows/ci.yml` de tu fork (lo vamos a reconstruir desde cero).

### 1. Primer pipeline (15 min)

Crea `.github/workflows/ci.yml` con el contenido de `etapas/01-ci-minimo.yml`, haz commit en `main`
y mira la ejecución en la pestaña **Actions**. Debe quedar en verde.

### 2. Lint y caché (15 min)

Reemplaza el contenido por `etapas/02-lint-y-cache.yml`. Ahora hay dos jobs y el de pruebas espera al de lint.

**Rómpelo a propósito:** agrega `import os` al inicio de `app/main.py` sin usarlo. El job de lint se
pone en rojo y el de pruebas ni arranca. Quita el import y vuelve a verde.

### 3. Matriz y cobertura (15 min)

Reemplaza por `etapas/03-matriz-y-cobertura.yml`. Las pruebas corren en paralelo en Python 3.12 y 3.13,
y al final de la ejecución puedes descargar el artefacto `cobertura`.

### 4. Quality gate del modelo (15 min)

Reemplaza por la versión final (la de este repo en `.github/workflows/ci.yml`).

**Rómpelo a propósito:** en `app/clasificador.py`, "optimiza" el vectorizador para que sea más liviano:

```python
("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), max_features=10)),
```

El lint pasa, las pruebas de código pasan, pero el job **Quality gate del modelo** se pone en rojo:
la exactitud cae de 100% a 56%. El código compila; lo que se rompió fue el comportamiento del modelo.

### 5. Protege `main` con un Pull Request (20 min)

1. **Settings → Branches → Add branch ruleset** (o *Add rule*): protege `main`, exige Pull Request y
   marca como obligatorios los checks `Lint y formato`, `Pruebas (Python 3.12)`, `Pruebas (Python 3.13)`
   y `Quality gate del modelo`.
2. Crea una rama `bug/validacion`, y en `app/clasificador.py` elimina las dos líneas que rechazan el
   texto vacío dentro de `normalizar`.
3. Abre un Pull Request hacia `main`. El pipeline corre solo, falla y GitHub bloquea el botón de merge.
4. Restaura las líneas en la misma rama: el PR se pone en verde y ya se puede integrar.

## Correr todo en tu máquina (opcional)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
ruff check . && ruff format --check .
pytest -v --cov=app
uvicorn app.main:app --reload     # y abre http://127.0.0.1:8000/docs
```

## Trabajo autónomo

- Agrega 5 ejemplos nuevos por categoría a `data/entrenamiento.csv` y verifica que el quality gate siga en verde.
- Sube el umbral a `0.90` en el workflow y observa si tu modelo lo aguanta.
- Agrega un job que construya la imagen Docker de la API (es el punto de partida de la Sesión 2: CD).
