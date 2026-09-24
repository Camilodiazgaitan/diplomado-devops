"""API mínima del clasificador de solicitudes de "Trámites al Día"."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.clasificador import Clasificador

app = FastAPI(title="Trámites al Día — clasificador de solicitudes")
clasificador = Clasificador()


class Solicitud(BaseModel):
    texto: str


@app.get("/health")
def health() -> dict:
    return {"estado": "ok"}


@app.post("/clasificar")
def clasificar(solicitud: Solicitud) -> dict:
    try:
        return clasificador.clasificar(solicitud.texto)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
