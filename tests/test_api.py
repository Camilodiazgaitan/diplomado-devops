"""Pruebas de integración: la API completa, como la llamaría el frontend."""

from fastapi.testclient import TestClient

from app.main import app

cliente = TestClient(app)


def test_health_responde_ok():
    respuesta = cliente.get("/health")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "ok"}


def test_clasificar_devuelve_categoria():
    respuesta = cliente.post("/clasificar", json={"texto": "quiero pagar la multa"})
    assert respuesta.status_code == 200
    assert respuesta.json()["categoria"] == "pago"


def test_clasificar_texto_vacio_da_422():
    respuesta = cliente.post("/clasificar", json={"texto": "  "})
    assert respuesta.status_code == 422
