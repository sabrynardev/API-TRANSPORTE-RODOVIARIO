from fastapi import FastAPI

from app.api.viagens import router as viagens_router


app = FastAPI(
    title="API de Normalização de Viagens",
    version="1.0.0"
)

app.include_router(viagens_router)