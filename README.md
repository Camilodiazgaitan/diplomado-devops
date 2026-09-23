# Laboratorio · Pipeline de CI para un clasificador con IA

**Módulo 4 · DevOps y CI/CD · Sesión 1** — Diplomado Automatización de Procesos con IA
Indra · UPTC · Tec de Monterrey · ProBoyacá

Este repositorio **no trae el pipeline hecho**. Trae la aplicación, sus pruebas y una lista de retos. El trabajo del equipo es construir el pipeline que la protege.

Se trabaja **en equipos de 3 o 4 personas** y **todo se hace desde el navegador**: no hay que instalar Git, ni Python, ni nada.

---

## La situación

"Trámites al Día" recibe miles de solicitudes escritas por los ciudadanos en texto libre: *"quiero pagar la multa"*, *"necesito un certificado de residencia"*. Un modelo de IA las clasifica en cuatro categorías y las manda a la cola correcta.

| Categoría | Ejemplo |
|---|---|
| `renovacion` | "se me venció el permiso y lo quiero renovar" |
| `certificado` | "necesito una constancia de residencia" |
| `pago` | "no aparece reflejado el pago que hice ayer" |
| `queja` | "llevo tres semanas esperando respuesta" |

La entidad quiere abrir el código a más desarrolladores, pero hoy nadie verifica nada antes de integrar un cambio. Ustedes son el equipo que va a montar esa verificación automática.

---

## Qué hay aquí

```
app/clasificador.py           el modelo (TF-IDF + regresión logística) y la limpieza del texto
app/main.py                   la API: GET /health y POST /clasificar
data/entrenamiento.csv        48 solicitudes etiquetadas con las que se entrena el modelo
data/evaluacion.csv           16 solicitudes que el modelo NUNCA ve al entrenar
tests/test_clasificador.py    pruebas unitarias (ya escritas)
tests/test_api.py             pruebas de la API (ya escritas)
requirements-dev.txt          todo lo necesario para correr pruebas y lint
.github/workflows/ci.yml      el esqueleto del pipeline, lleno de TODOs: esto es lo que hay que resolver
```

---

## Cómo se trabaja

- **Un repositorio por equipo.** Una sola persona del equipo pulsa arriba **Use this template → Create a new repository**, con visibilidad **Public** (en repositorios públicos Actions no tiene costo). Luego, en **Settings → Collaborators**, invita a los demás del equipo.
- **Roles que rotan en cada reto.** Uno maneja la pantalla y escribe, otro lee la documentación oficial y el tercero revisa el resultado y decide si el reto está cumplido. Cambien de rol en cada reto.
- **Cada reto tiene un criterio de aceptación.** No es "quedó bonito": es una condición concreta que se ve en la pestaña Actions.
- **La documentación oficial es parte del laboratorio:** https://docs.github.com/actions. Buscar ahí es exactamente lo que van a hacer en su trabajo real.

---

## Reto 0 · Reconocimiento (10 min)

Antes de tocar el pipeline, entiendan qué están protegiendo.

1. Creen el repositorio del equipo e inviten a los demás.
2. Abran `app/clasificador.py` y `tests/test_clasificador.py`. ¿Qué verifica cada prueba?
3. Abran `.github/workflows/ci.yml`. Está casi vacío, con comentarios `TODO`.
4. Vayan a la pestaña **Actions**, pulsen el workflow **CI → Run workflow**. Corre, pero no verifica nada todavía.

**Criterio de aceptación:** el equipo puede explicar en una frase qué hace la aplicación y por qué el pipeline actual no sirve de nada.

> Si en vez de "Use this template" hicieron **Fork**, GitHub deja los workflows desactivados: hay que entrar a Actions y pulsar *"I understand my workflows, go ahead and enable them"*.

---

## Reto 1 · Que las pruebas corran solas (20 min)

Completen `.github/workflows/ci.yml` para que, **en cada push a `main` y en cada Pull Request**, el pipeline instale las dependencias y corra las pruebas.

**Criterio de aceptación:**

- Hacen un cambio cualquiera (por ejemplo, una línea en este README), commit, y en la pestaña Actions aparece una ejecución **sin que nadie la lance a mano**.
- El log del último paso dice `8 passed`.

**Pistas**

- El runner nace vacío: el primer paso siempre es traer el código.
- Las acciones que van a necesitar son `actions/checkout` y `actions/setup-python`. Usen la versión `v7`.
- Las dependencias están en `requirements-dev.txt`.
- El comando de pruebas es `pytest -v`.

**Comprobación extra:** rompan una prueba a propósito (cambien un valor esperado en `tests/test_api.py`), hagan commit y confirmen que el pipeline se pone en rojo solo. Después devuélvanlo.

---

## Reto 2 · Revisar el estilo antes de gastar tiempo (15 min)

Agreguen un **segundo job** llamado `Lint y formato` que corra `ruff` sobre el código, y háganlo de manera que **si el lint falla, las pruebas ni siquiera arranquen**.

**Criterio de aceptación:**

- Agregan `import os` al inicio de `app/main.py` sin usarlo y hacen commit.
- En Actions: el job de lint aparece en rojo en menos de 30 segundos y el de pruebas aparece como **omitido** (skipped), no como fallido.

**Pistas**

- Los comandos son `ruff check .` y `ruff format --check .`.
- Instalen la herramienta con la versión fija: `pip install ruff==0.15.11`. Si la dejan libre, el día que salga una versión nueva el pipeline se pone rojo solo. Ese es un problema real, no una manía.
- Busquen en la documentación qué palabra hace que un job espere a otro.
- Mientras estén ahí, busquen qué hace `cache: pip` dentro de `setup-python` y mídanlo: comparen el tiempo del paso de instalación entre dos ejecuciones seguidas.

---

## Reto 3 · Dos versiones de Python y cobertura mínima (15 min)

El área de infraestructura va a migrar a Python 3.13 el próximo trimestre y nadie sabe si el código aguanta. Hagan que **el mismo job de pruebas corra en 3.12 y en 3.13**, en paralelo, y que el pipeline **falle si la cobertura baja del 80%**.

**Criterio de aceptación:**

- En Actions se ven dos jobs de pruebas, uno por versión, corriendo al mismo tiempo.
- El log muestra el porcentaje de cobertura.
- Al terminar la ejecución, se puede **descargar** el reporte de cobertura desde la página de la ejecución.

**Pistas**

- Busquen `strategy.matrix` en la documentación de GitHub Actions.
- `pytest` acepta `--cov=app`, `--cov-report=xml` y `--cov-fail-under`.
- Para dejar un archivo descargable existe `actions/upload-artifact@v7`.

**Para discutir en el equipo:** la cobertura mide qué líneas se ejecutaron durante las pruebas. ¿Eso garantiza que las pruebas sirvan? Escriban su respuesta en el README de su repositorio.

---

## Reto 4 · El quality gate del modelo (25 min) — el reto principal

Todo lo anterior protege el **código**. Este reto protege el **modelo**, y es lo que diferencia un pipeline de software tradicional de uno para una solución con IA.

En `data/evaluacion.csv` hay 16 solicitudes con su categoría correcta. El modelo **nunca las ve** al entrenar. Escriban una prueba nueva, `tests/test_calidad_modelo.py`, que clasifique esas 16 solicitudes, calcule el porcentaje de aciertos y **falle si baja del 80%**. Después agreguen al pipeline un tercer job, `Quality gate del modelo`, que corra solo esa prueba después de que pasen las demás.

**Criterio de aceptación:**

1. Con el código como está, el job pasa y el log muestra la exactitud obtenida.
2. Alguien del equipo aplica este cambio en `app/clasificador.py`:

```python
            ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), max_features=10)),
```

   Al hacer commit, el lint pasa, las pruebas de código pasan en las dos versiones de Python, **y el quality gate se pone en rojo**. El equipo puede explicar por qué las otras pruebas no lo detectaron.

3. Devuelven el cambio y todo vuelve a verde.

**Pistas**

- En `app/clasificador.py` ya existe `cargar_datos("evaluacion.csv")` y la clase `Clasificador` con su método `clasificar`, que devuelve un diccionario con la categoría.
- El umbral no debería estar escrito a mano dentro de la prueba: léanlo de una variable de entorno con valor por defecto, y definan esa variable en el workflow. Así el umbral se sube sin tocar el código.
- Para que el job corra **solo** esa prueba: `pytest -v -s tests/test_calidad_modelo.py`. Y para que los otros jobs no la repitan: `--ignore=tests/test_calidad_modelo.py`.

**Para discutir:** ¿quién decide el umbral, el equipo técnico o el dueño del trámite? ¿Qué pasa si se pone en 95%?

---

## Reto 5 · Que nadie pueda integrar en rojo (20 min)

Hasta aquí cualquiera puede hacer commit directo a `main` aunque el pipeline esté fallando. Ciérrenlo.

Configuren el repositorio para que **todo cambio entre por Pull Request** y solo se pueda integrar si los cuatro checks están en verde. Después demuéstrenlo:

1. Creen la rama `bug/validacion`.
2. En `app/clasificador.py`, dentro de `normalizar`, borren las dos líneas que rechazan el texto vacío.
3. Abran el Pull Request hacia `main`.

**Criterio de aceptación:**

- El pipeline corre solo sobre el Pull Request, dos pruebas fallan y el botón **Merge pull request** queda bloqueado.
- Al restaurar las líneas en la misma rama, el PR pasa a verde y el merge se habilita.

**Pistas**

- **Settings → Rules → Rulesets → New branch ruleset**, objetivo: la rama por defecto.
- GitHub solo deja marcar como obligatorio un check que ya haya corrido alguna vez con ese nombre exacto. Por eso este reto va de último.

---

## Qué entrega cada equipo

Al final de la sesión, en el chat:

1. El enlace de su repositorio.
2. Una captura de una ejecución en rojo y una en verde.
3. Las dos respuestas escritas: la de cobertura (reto 3) y la del umbral (reto 4).

---

## Si algo se rompe

| Síntoma | Qué revisar |
|---|---|
| No aparece ninguna ejecución en Actions | El archivo debe llamarse exactamente `.github/workflows/ci.yml`. Si hicieron Fork, falta habilitar los workflows |
| "Workflow file issue" o error de YAML | La indentación. En YAML los espacios importan y no se admiten tabuladores |
| Falla al instalar dependencias | Revisen que el paso de checkout esté antes y que el archivo sea `requirements-dev.txt` |
| No encuentro los checks al crear la regla | Deben haber corrido al menos una vez con ese nombre |
| Quiero repetir una ejecución | Entren a la ejecución y pulsen **Re-run jobs** |

---

## Trabajo autónomo (después de la sesión)

1. Agreguen cinco ejemplos nuevos por categoría a `data/entrenamiento.csv` y verifiquen que el quality gate siga en verde.
2. Suban el umbral a 0.90 y vean si el modelo lo aguanta.
3. Agreguen un job que construya la imagen Docker de la API con `docker build`. Ese es el punto de partida de la Sesión 2: entrega continua.
