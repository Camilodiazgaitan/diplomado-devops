"""Clasificador de solicitudes ciudadanas para "Trámites al Día".

Recibe el texto libre que escribe el ciudadano y devuelve la categoría
del trámite (renovacion, certificado, pago, queja) para enrutarlo a la
cola correcta. Es un modelo pequeño (TF-IDF + regresión logística) para
que el laboratorio corra en segundos dentro del pipeline de CI.
"""

import csv
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CATEGORIAS = ("renovacion", "certificado", "pago", "queja")


def cargar_datos(nombre_archivo: str) -> tuple[list[str], list[str]]:
    """Lee un CSV con columnas texto,categoria."""
    textos, etiquetas = [], []
    with open(DATA_DIR / nombre_archivo, encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            textos.append(fila["texto"])
            etiquetas.append(fila["categoria"])
    return textos, etiquetas


def entrenar() -> Pipeline:
    """Entrena el modelo con data/entrenamiento.csv."""
    textos, etiquetas = cargar_datos("entrenamiento.csv")
    modelo = Pipeline(
        [
            ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5))),
            ("clf", LogisticRegression(max_iter=1000, random_state=42)),
        ]
    )
    modelo.fit(textos, etiquetas)
    return modelo


def normalizar(texto: str) -> str:
    """Limpia el texto antes de clasificarlo."""
    if not texto or not texto.strip():
        raise ValueError("El texto de la solicitud no puede estar vacío")
    return " ".join(texto.lower().split())


class Clasificador:
    def __init__(self) -> None:
        self.modelo = entrenar()

    def clasificar(self, texto: str) -> dict:
        limpio = normalizar(texto)
        probabilidades = self.modelo.predict_proba([limpio])[0]
        clases = list(self.modelo.classes_)
        mejor = max(range(len(clases)), key=lambda i: probabilidades[i])
        return {
            "categoria": clases[mejor],
            "confianza": round(float(probabilidades[mejor]), 3),
        }
