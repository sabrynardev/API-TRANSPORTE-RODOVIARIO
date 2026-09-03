from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1/viagens",
    tags=["Viagens"],
)

@router.post("/normalizar")
def normalizar_viagem():
    return {
        "message": "Viagem normalizada com sucesso!"
    }