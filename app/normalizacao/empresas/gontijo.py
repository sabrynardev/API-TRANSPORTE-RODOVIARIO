from datetime import datetime
from zoneinfo import ZoneInfo

from app.domain.exceptions import ErroNormalizacao
from app.domain.models import (
    Localidade,
    Preco,
    ViagemNormalizada,
)
from app.domain.validacoes import (
    aplicar_fuso_padrao,
    validar_assentos,
    validar_campos_obrigatorios,
    validar_categoria,
    validar_duracao,
    validar_ordem_datas,
    validar_preco,
    validar_uf,
)
from app.normalizacao.interface import NormalizadorViagem


class NormalizadorGontijo(NormalizadorViagem):

    def reconhece(self, payload: dict) -> bool:
        return "serviceCode" in payload

    def normalizar(
        self,
        payload: dict,
    ) -> ViagemNormalizada:

        empresa = "Gontijo"

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
            raise ErroNormalizacao(
                mensagem="Campo obrigatório ausente.",
                campo=erro.args[0],
                empresa_identificada=empresa,
            )

        fuso_bahia = ZoneInfo(
            "America/Bahia"
        )

        try:
            partida = datetime.fromisoformat(
                payload["departure"].replace(
                    "Z",
                    "+00:00",
                )
            )

            partida = aplicar_fuso_padrao(
                partida
            )

            partida = partida.astimezone(
                fuso_bahia
            )

        except (
            ValueError,
            TypeError,
            AttributeError,
        ):
            raise ErroNormalizacao(
                mensagem="Data de saída inválida.",
                campo="departure",
                empresa_identificada=empresa,
            )

        try:
            chegada = datetime.fromisoformat(
                payload["arrival"].replace(
                    "Z",
                    "+00:00",
                )
            )

            chegada = aplicar_fuso_padrao(
                chegada
            )

            chegada = chegada.astimezone(
                fuso_bahia
            )

        except (
            ValueError,
            TypeError,
            AttributeError,
        ):
            raise ErroNormalizacao(
                mensagem="Data de chegada inválida.",
                campo="arrival",
                empresa_identificada=empresa,
            )

        try:
            validar_ordem_datas(
                partida,
                chegada,
            )

        except ValueError as erro:
            raise ErroNormalizacao(
                mensagem=str(erro),
                campo="arrival",
                empresa_identificada=empresa,
            )

        try:
            duracao_segundos = int(
                payload[
                    "estimatedDurationSeconds"
                ]
            )

            duracao_minutos = (
                duracao_segundos // 60
            )

        except (ValueError, TypeError):
            raise ErroNormalizacao(
                mensagem="Duração inválida.",
                campo="estimatedDurationSeconds",
                empresa_identificada=empresa,
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
                empresa_identificada=empresa,
            )

        try:
            valor = float(
                payload["fare"]["amount"]
            )

            validar_preco(valor)

        except (
            ValueError,
            TypeError,
            KeyError,
        ) as erro:
            mensagem = str(erro)

            if not mensagem or isinstance(
                erro,
                KeyError,
            ):
                mensagem = "Preço inválido."

            raise ErroNormalizacao(
                mensagem=mensagem,
                campo="fare.amount",
                empresa_identificada=empresa,
            )

        try:
            assentos = int(
                payload["availableSeats"]
            )

            validar_assentos(assentos)

        except (ValueError, TypeError) as erro:
            mensagem = str(erro)

            if not mensagem:
                mensagem = (
                    "Quantidade de assentos inválida."
                )

            raise ErroNormalizacao(
                mensagem=mensagem,
                campo="availableSeats",
                empresa_identificada=empresa,
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
                empresa_identificada=empresa,
            )

        try:
            cidade_origem = (
                payload["from"]["city"]
            )

            uf_origem = (
                payload["from"]["state"]
            )

            cidade_destino = (
                payload["to"]["city"]
            )

            uf_destino = (
                payload["to"]["state"]
            )

        except (KeyError, TypeError):
            raise ErroNormalizacao(
                mensagem="Campo obrigatório ausente.",
                campo="from/to",
                empresa_identificada=empresa,
            )

        try:
            validar_uf(uf_origem)

        except ValueError as erro:
            raise ErroNormalizacao(
                mensagem=str(erro),
                campo="from.state",
                empresa_identificada=empresa,
            )

        try:
            validar_uf(uf_destino)

        except ValueError as erro:
            raise ErroNormalizacao(
                mensagem=str(erro),
                campo="to.state",
                empresa_identificada=empresa,
            )

        try:
            moeda = payload["fare"]["currency"]

        except (KeyError, TypeError):
            raise ErroNormalizacao(
                mensagem="Campo obrigatório ausente.",
                campo="fare.currency",
                empresa_identificada=empresa,
            )

        return ViagemNormalizada(
            id_viagem=payload["serviceCode"],
            empresa=empresa,
            origem=Localidade(
                cidade=cidade_origem,
                uf=uf_origem,
            ),
            destino=Localidade(
                cidade=cidade_destino,
                uf=uf_destino,
            ),
            partida=partida.isoformat(),
            chegada=chegada.isoformat(),
            duracao_minutos=duracao_minutos,
            preco=Preco(
                valor=valor,
                moeda=moeda,
            ),
            categoria=categoria,
            assentos_disponiveis=assentos,
        )