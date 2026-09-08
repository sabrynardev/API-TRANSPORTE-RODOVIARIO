from datetime import datetime
from zoneinfo import ZoneInfo

from app.domain.models import Localidade, Preco, ViagemNormalizada
from app.normalizacao.interface import NormalizadorViagem
from app.domain.validacoes import (
    validar_ordem_datas,
    validar_duracao,
    validar_preco,
    validar_assentos,
)


# A Progresso é uma implementação concreta do contrato
# NormalizadorViagem criado na TASK-06.
# Por isso, ela precisa implementar:
# - reconhece()
# - normalizar()


class NormalizadorProgresso(NormalizadorViagem):

    def reconhece(self, payload: dict) -> bool:
        campos_identificadores = {
            "codigoViagem",
            "cidadeOrigem",
            "ufOrigem",
            "cidadeDestino",
            "ufDestino",
            "dataHoraSaida",
            "dataHoraChegada",
            "valorPassagem",
            "tipoServico",
            "assentosDisponiveis",
        }

        return campos_identificadores.issubset(payload.keys())

    def normalizar(self, payload: dict) -> ViagemNormalizada:
        fuso = ZoneInfo(
            payload.get(
                "fusoHorario",
                "America/Bahia"
            )
        )

        partida = datetime.strptime(
            payload["dataHoraSaida"],
            "%d/%m/%Y %H:%M"
        ).replace(tzinfo=fuso)

        chegada = datetime.strptime(
            payload["dataHoraChegada"],
            "%d/%m/%Y %H:%M"
        ).replace(tzinfo=fuso)

        validar_ordem_datas(
            partida,
            chegada,
        )

        horas, minutos = map(
            int,
            payload["tempoEstimado"].split(":")
        )

        duracao_minutos = (
            horas * 60
        ) + minutos

        validar_duracao(
            partida,
            chegada,
            duracao_minutos,
        )

        valor = float(
            payload["valorPassagem"].replace(
                ",",
                "."
            )
        )

        validar_preco(valor)

        assentos = int(
            payload["assentosDisponiveis"]
        )

        validar_assentos(assentos)

        return ViagemNormalizada(
            id_viagem=payload["codigoViagem"],

            empresa="Auto Viação Progresso",

            origem=Localidade(
                cidade=payload["cidadeOrigem"],
                uf=payload["ufOrigem"],
            ),

            destino=Localidade(
                cidade=payload["cidadeDestino"],
                uf=payload["ufDestino"],
            ),

            partida=partida.isoformat(),

            chegada=chegada.isoformat(),

            duracao_minutos=duracao_minutos,

            preco=Preco(
                valor=valor,
                moeda="BRL",
            ),

            categoria=payload[
                "tipoServico"
            ].lower(),

            assentos_disponiveis=assentos,
        )