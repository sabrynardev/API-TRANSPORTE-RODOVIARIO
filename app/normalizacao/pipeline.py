from app.domain.models import ViagemNormalizada
from app.normalizacao.registry import NormalizadorRegistry

class PipelineNormalizacao:
    def __init__(self, registry: NormalizadorRegistry):
        self._registry = registry

    def processar(self, payload: dict) -> ViagemNormalizada:
        normalizador = self._registry.resolver(payload)
        if normalizador is None:
            raise ValueError("Nenhum normalizador encontrado para o payload fornecido.")
        return normalizador.normalizar(payload)