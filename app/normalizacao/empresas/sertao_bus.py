from datetime import datetime

from app.domain.models import Localidade, Preco, ViagemNormalizada
from app.domain.exceptions import ErroNormalizacao
from app.normalizacao.interface import NormalizadorViagem
from app.domain.validacoes import (
    validar_ordem_datas,
    validar_duracao,
    validar_preco,
    validar_assentos,
    validar_categoria,
    validar_campos_obrigatorios,
)


class NormalizadorSertaoBus(NormalizadorViagem):

    def reconhece(self, payload: dict) -> bool:
        return "numero" in payload

    def normalizar(self, payload: dict) -> ViagemNormalizada:
        campos_obrigatorios = [
            "numero",
            "rota",
            "horarios",
            "duracao_horas",
            "preco_total",
            "moeda",
            "servico",
            "lugares_livres",
        ]

        try:
            validar_campos_obrigatorios(
                payload,
                campos_obrigatorios,
            )
        except KeyError as erro:
            campo = erro.args[0]

            raise ErroNormalizacao(
                mensagem="Campo obrigatório ausente.",
                campo=campo,
                empresa_identificada="Sertão Bus",
            )

        try:
            origem_cidade, origem_uf = (
                payload["rota"]["partida"].rsplit("/", 1)
            )
        except (ValueError, AttributeError, KeyError):
            raise ErroNormalizacao(
                mensagem="A origem informada possui formato inválido.",
                campo="rota.partida",
                empresa_identificada="Sertão Bus",
            )

        try:
            destino_cidade, destino_uf = (
                payload["rota"]["chegada"].rsplit("/", 1)
            )
        except (ValueError, AttributeError, KeyError):
            raise ErroNormalizacao(
                mensagem="O destino informado possui formato inválido.",
                campo="rota.chegada",
                empresa_identificada="Sertão Bus",
            )

        try:
            partida = datetime.fromisoformat(
                payload["horarios"]["saida"]
            )
        except (ValueError, TypeError, KeyError):
            raise ErroNormalizacao(
                mensagem="A data de saída possui formato inválido.",
                campo="horarios.saida",
                empresa_identificada="Sertão Bus",
            )

        try:
            chegada = datetime.fromisoformat(
                payload["horarios"]["chegada"]
            )
        except (ValueError, TypeError, KeyError):
            raise ErroNormalizacao(
                mensagem="A data de chegada possui formato inválido.",
                campo="horarios.chegada",
                empresa_identificada="Sertão Bus",
            )

        try:
            validar_ordem_datas(partida, chegada)
        except ValueError as erro:
            raise ErroNormalizacao(
                mensagem=str(erro),
                campo="horarios.chegada",
                empresa_identificada="Sertão Bus",
            )

        try:
            duracao_minutos = int(
                float(payload["duracao_horas"]) * 60
            )
        except (ValueError, TypeError):
            raise ErroNormalizacao(
                mensagem="A duração informada é inválida.",
                campo="duracao_horas",
                empresa_identificada="Sertão Bus",
            )

        try:
            validar_duracao(
                partida,
                chegada,
                duracao_minutos,
            )
        except ValueError as erro:
            raise ErroNormalizacao(
                mensagem=str(erro),
                campo="duracao_horas",
                empresa_identificada="Sertão Bus",
            )

        try:
            valor = float(
                payload["preco_total"]
            )
        except (ValueError, TypeError):
            raise ErroNormalizacao(
                mensagem="O preço informado é inválido.",
                campo="preco_total",
                empresa_identificada="Sertão Bus",
            )

        try:
            validar_preco(valor)
        except ValueError as erro:
            raise ErroNormalizacao(
                mensagem=str(erro),
                campo="preco_total",
                empresa_identificada="Sertão Bus",
            )

        try:
            assentos = int(
                payload["lugares_livres"]
            )
        except (ValueError, TypeError):
            raise ErroNormalizacao(
                mensagem="A quantidade de assentos disponíveis é inválida.",
                campo="lugares_livres",
                empresa_identificada="Sertão Bus",
            )

        try:
            validar_assentos(assentos)
        except ValueError as erro:
            raise ErroNormalizacao(
                mensagem=str(erro),
                campo="lugares_livres",
                empresa_identificada="Sertão Bus",
            )

        categorias = {
            "CONV": "convencional",
            "EXEC": "executivo",
            "SEMI": "semileito",
            "LEITO": "leito",
        }

        categoria = categorias.get(
            payload["servico"]
        )

        try:
            validar_categoria(categoria)
        except ValueError as erro:
            raise ErroNormalizacao(
                mensagem=str(erro),
                campo="servico",
                empresa_identificada="Sertão Bus",
            )

        return ViagemNormalizada(
            id_viagem=payload["numero"],
            empresa="Sertão Bus",
            origem=Localidade(
                cidade=origem_cidade,
                uf=origem_uf,
            ),
            destino=Localidade(
                cidade=destino_cidade,
                uf=destino_uf,
            ),
            partida=partida.isoformat(),
            chegada=chegada.isoformat(),
            duracao_minutos=duracao_minutos,
            preco=Preco(
                valor=valor,
                moeda=payload["moeda"],
            ),
            categoria=categoria,
            assentos_disponiveis=assentos,
        )