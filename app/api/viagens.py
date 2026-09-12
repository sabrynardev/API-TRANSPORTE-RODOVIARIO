from fastapi import APIRouter, HTTPException

from app.domain.exceptions import ErroNormalizacao
from app.domain.models import RespostaNormalizacao
from app.normalizacao.pipeline import PipelineNormalizacao
from app.normalizacao.registry import NormalizadorRegistry

from app.normalizacao.empresas.progresso import NormalizadorProgresso
from app.normalizacao.empresas.rota import NormalizadorRota
from app.normalizacao.empresas.gontijo import NormalizadorGontijo
from app.normalizacao.empresas.sertao_bus import NormalizadorSertaoBus


router = APIRouter(
    prefix="/api/v1/viagens",
    tags=["Viagens"],
)


registry = NormalizadorRegistry()

registry.registrar(NormalizadorProgresso())
registry.registrar(NormalizadorRota())
registry.registrar(NormalizadorGontijo())
registry.registrar(NormalizadorSertaoBus())

pipeline = PipelineNormalizacao(registry)


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
            viagem = pipeline.processar(payload)
            viagens_normalizadas.append(viagem)

        except ErroNormalizacao as erro:
            raise HTTPException(
                status_code=422,
                detail={
                    "indice": indice,
                    "empresa_identificada": erro.empresa_identificada,
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
        total=len(viagens_normalizadas),
        viagens=viagens_normalizadas,
    )