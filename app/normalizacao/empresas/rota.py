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


class NormalizadorRota(NormalizadorViagem):

    def reconhece(self, payload: dict) -> bool:
        return "trip_id" in payload

    def normalizar(self, payload: dict) -> ViagemNormalizada:
        campos_obrigatorios = [
            "trip_id",
            "origem",
            "destino",
            "partida_em",
            "chegada_em",
            "duracao_minutos",
            "tarifa_centavos",
            "moeda",
            "classe",
            "vagas",
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
                empresa_identificada="Rota Transportes",
            )

        try:
            partida = datetime.fromisoformat(
                payload["partida_em"]
            )
        except ValueError:
            raise ErroNormalizacao(
                mensagem="A data de saída possui formato inválido.",
                campo="partida_em",
                empresa_identificada="Rota Transportes",
            )

        try:
            chegada = datetime.fromisoformat(
                payload["chegada_em"]
            )
        except ValueError:
            raise ErroNormalizacao(
                mensagem="A data de chegada possui formato inválido.",
                campo="chegada_em",
                empresa_identificada="Rota Transportes",
            )

        try:
            validar_ordem_datas(partida, chegada)
        except ValueError as erro:
            raise ErroNormalizacao(
                mensagem=str(erro),
                campo="chegada_em",
                empresa_identificada="Rota Transportes",
            )

        try:
            duracao_minutos = int(
                payload["duracao_minutos"]
            )
        except (ValueError, TypeError):
            raise ErroNormalizacao(
                mensagem="A duração informada é inválida.",
                campo="duracao_minutos",
                empresa_identificada="Rota Transportes",
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
                campo="duracao_minutos",
                empresa_identificada="Rota Transportes",
            )

        try:
            valor = payload["tarifa_centavos"] / 100
        except (TypeError, ValueError):
            raise ErroNormalizacao(
                mensagem="O preço informado é inválido.",
                campo="tarifa_centavos",
                empresa_identificada="Rota Transportes",
            )

        try:
            validar_preco(valor)
        except ValueError as erro:
            raise ErroNormalizacao(
                mensagem=str(erro),
                campo="tarifa_centavos",
                empresa_identificada="Rota Transportes",
            )

        try:
            assentos = int(payload["vagas"])
        except (ValueError, TypeError):
            raise ErroNormalizacao(
                mensagem="A quantidade de assentos disponíveis é inválida.",
                campo="vagas",
                empresa_identificada="Rota Transportes",
            )

        try:
            validar_assentos(assentos)
        except ValueError as erro:
            raise ErroNormalizacao(
                mensagem=str(erro),
                campo="vagas",
                empresa_identificada="Rota Transportes",
            )

        try:
            categoria = payload["classe"].lower()
        except AttributeError:
            raise ErroNormalizacao(
                mensagem="A categoria informada não pode ser normalizada.",
                campo="classe",
                empresa_identificada="Rota Transportes",
            )

        try:
            validar_categoria(categoria)
        except ValueError as erro:
            raise ErroNormalizacao(
                mensagem=str(erro),
                campo="classe",
                empresa_identificada="Rota Transportes",
            )

        return ViagemNormalizada(
            id_viagem=payload["trip_id"],
            empresa="Rota Transportes",
            origem=Localidade(
                cidade=payload["origem"]["municipio"],
                uf=payload["origem"]["estado"],
            ),
            destino=Localidade(
                cidade=payload["destino"]["municipio"],
                uf=payload["destino"]["estado"],
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