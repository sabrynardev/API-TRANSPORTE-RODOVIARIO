from datetime import datetime
from zoneinfo import ZoneInfo

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


class NormalizadorGontijo(NormalizadorViagem):

    def reconhece(self, payload: dict) -> bool:
        return "serviceCode" in payload

    def normalizar(self, payload: dict) -> ViagemNormalizada:
        campos_obrigatorios = [
            "serviceCode",
            "from",
            "to",
            "departure",
            "arrival",
            "estimatedDurationSeconds",
            "fare",
            "serviceClass",
            "availableSeats",
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
                empresa_identificada="Gontijo",
            )

        fuso_bahia = ZoneInfo("America/Bahia")

        try:
            partida = datetime.fromisoformat(
                payload["departure"].replace(
                    "Z",
                    "+00:00",
                )
            ).astimezone(fuso_bahia)
        except (ValueError, AttributeError):
            raise ErroNormalizacao(
                mensagem="A data de saída possui formato inválido.",
                campo="departure",
                empresa_identificada="Gontijo",
            )

        try:
            chegada = datetime.fromisoformat(
                payload["arrival"].replace(
                    "Z",
                    "+00:00",
                )
            ).astimezone(fuso_bahia)
        except (ValueError, AttributeError):
            raise ErroNormalizacao(
                mensagem="A data de chegada possui formato inválido.",
                campo="arrival",
                empresa_identificada="Gontijo",
            )

        try:
            validar_ordem_datas(partida, chegada)
        except ValueError as erro:
            raise ErroNormalizacao(
                mensagem=str(erro),
                campo="arrival",
                empresa_identificada="Gontijo",
            )

        try:
            duracao_minutos = (
                int(
                    payload["estimatedDurationSeconds"]
                ) // 60
            )
        except (ValueError, TypeError):
            raise ErroNormalizacao(
                mensagem="A duração informada é inválida.",
                campo="estimatedDurationSeconds",
                empresa_identificada="Gontijo",
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
                campo="estimatedDurationSeconds",
                empresa_identificada="Gontijo",
            )

        try:
            valor = float(
                payload["fare"]["amount"]
            )
        except (ValueError, TypeError, KeyError):
            raise ErroNormalizacao(
                mensagem="O preço informado é inválido.",
                campo="fare.amount",
                empresa_identificada="Gontijo",
            )

        try:
            validar_preco(valor)
        except ValueError as erro:
            raise ErroNormalizacao(
                mensagem=str(erro),
                campo="fare.amount",
                empresa_identificada="Gontijo",
            )

        try:
            assentos = int(
                payload["availableSeats"]
            )
        except (ValueError, TypeError):
            raise ErroNormalizacao(
                mensagem="A quantidade de assentos disponíveis é inválida.",
                campo="availableSeats",
                empresa_identificada="Gontijo",
            )

        try:
            validar_assentos(assentos)
        except ValueError as erro:
            raise ErroNormalizacao(
                mensagem=str(erro),
                campo="availableSeats",
                empresa_identificada="Gontijo",
            )

        categorias = {
            "CONVENTIONAL": "convencional",
            "EXECUTIVE": "executivo",
            "SEMI_SLEEPER": "semileito",
            "SLEEPER": "leito",
        }

        categoria = categorias.get(
            payload["serviceClass"]
        )

        try:
            validar_categoria(categoria)
        except ValueError as erro:
            raise ErroNormalizacao(
                mensagem=str(erro),
                campo="serviceClass",
                empresa_identificada="Gontijo",
            )

        return ViagemNormalizada(
            id_viagem=payload["serviceCode"],
            empresa="Gontijo",
            origem=Localidade(
                cidade=payload["from"]["city"],
                uf=payload["from"]["state"],
            ),
            destino=Localidade(
                cidade=payload["to"]["city"],
                uf=payload["to"]["state"],
            ),
            partida=partida.isoformat(),
            chegada=chegada.isoformat(),
            duracao_minutos=duracao_minutos,
            preco=Preco(
                valor=valor,
                moeda=payload["fare"]["currency"],
            ),
            categoria=categoria,
            assentos_disponiveis=assentos,
        )