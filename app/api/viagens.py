from fastapi import APIRouter, HTTPException

from app.domain.exceptions import ErroNormalizacao
from app.domain.models import RespostaNormalizacao
from app.normalizacao.configuracao import pipeline_normalizacao


router = APIRouter(
    prefix="/api/v1/viagens",
    tags=["Viagens"],
)


@router.post(
    "/normalizar",
    response_model=RespostaNormalizacao,
)
def normalizar_viagens(
    payloads: list[dict],
) -> RespostaNormalizacao:

    viagens_normalizadas = []

    for indice, payload in enumerate(payloads):
        try:
            viagem = pipeline_normalizacao.processar(
                payload
            )

            viagens_normalizadas.append(
                viagem
            )

        except ErroNormalizacao as erro:
            raise HTTPException(
                status_code=422,
                detail={
                    "indice": indice,
                    "empresa_identificada": (
                        erro.empresa_identificada
                    ),
                    "campo": erro.campo,
                    "mensagem": erro.mensagem,
                },
            )

        except ValueError as erro:
            raise HTTPException(
                status_code=422,
                detail={
                    "indice": indice,
                    "empresa_identificada": None,
                    "campo": None,
                    "mensagem": str(erro),
                },
            )

    return RespostaNormalizacao(
        total=len(
            viagens_normalizadas
        ),
        viagens=viagens_normalizadas,
    )