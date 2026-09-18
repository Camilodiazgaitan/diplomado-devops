"""Pruebas unitarias: lógica pura, sin levantar la API."""

import pytest

from app.clasificador import CATEGORIAS, Clasificador, normalizar


@pytest.fixture(scope="module")
def clasificador():
    return Clasificador()


def test_normalizar_quita_espacios_y_mayusculas():
    assert normalizar("  Quiero   PAGAR la multa ") == "quiero pagar la multa"


def test_normalizar_rechaza_texto_vacio():
    with pytest.raises(ValueError):
        normalizar("   ")


def test_respuesta_tiene_categoria_valida(clasificador):
    resultado = clasificador.clasificar("necesito un certificado de residencia")
    assert resultado["categoria"] in CATEGORIAS
    assert 0 <= resultado["confianza"] <= 1


@pytest.mark.parametrize(
    "texto, esperada",
    [
        ("quiero renovar mi licencia vencida", "renovacion"),
        ("cómo pago el impuesto predial", "pago"),
        ("presento una queja por la demora", "queja"),
    ],
)
def test_casos_obvios(clasificador, texto, esperada):
    assert clasificador.clasificar(texto)["categoria"] == esperada
