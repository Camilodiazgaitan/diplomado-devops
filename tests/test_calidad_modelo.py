"""Quality gate del modelo: si la exactitud cae por debajo del umbral, el
pipeline se pone en rojo aunque todo el código compile y los demás tests
pasen. Es la diferencia entre CI para software y CI para soluciones con IA."""

import os

from app.clasificador import Clasificador, cargar_datos

UMBRAL_EXACTITUD = float(os.getenv("UMBRAL_EXACTITUD", "0.80"))


def test_exactitud_minima_en_datos_de_evaluacion():
    clasificador = Clasificador()
    textos, esperadas = cargar_datos("evaluacion.csv")
    aciertos = sum(
        clasificador.clasificar(t)["categoria"] == e for t, e in zip(textos, esperadas, strict=True)
    )
    exactitud = aciertos / len(textos)
    mensaje = f"Exactitud del modelo: {exactitud:.2%} (umbral {UMBRAL_EXACTITUD:.0%})"
    print(f"\n{mensaje}")
    # En GitHub Actions, deja el resultado visible en el resumen de la ejecución
    resumen = os.getenv("GITHUB_STEP_SUMMARY")
    if resumen:
        with open(resumen, "a", encoding="utf-8") as f:
            icono = "✅" if exactitud >= UMBRAL_EXACTITUD else "❌"
            f.write(f"### {icono} Quality gate del modelo\n\n{mensaje}\n")
    assert exactitud >= UMBRAL_EXACTITUD, (
        f"Exactitud {exactitud:.2%} por debajo del umbral {UMBRAL_EXACTITUD:.0%}"
    )
