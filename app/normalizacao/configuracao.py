from app.normalizacao.empresas.gontijo import NormalizadorGontijo
from app.normalizacao.empresas.progresso import NormalizadorProgresso
from app.normalizacao.empresas.rota import NormalizadorRota
from app.normalizacao.empresas.sertao_bus import NormalizadorSertaoBus
from app.normalizacao.pipeline import PipelineNormalizacao
from app.normalizacao.registry import NormalizadorRegistry


def criar_pipeline_normalizacao() -> PipelineNormalizacao:
    registry = NormalizadorRegistry()

    registry.registrar(NormalizadorProgresso())
    registry.registrar(NormalizadorRota())
    registry.registrar(NormalizadorGontijo())
    registry.registrar(NormalizadorSertaoBus())

    return PipelineNormalizacao(registry)


pipeline_normalizacao = criar_pipeline_normalizacao()