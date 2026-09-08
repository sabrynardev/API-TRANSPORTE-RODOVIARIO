from datetime import datetime

from app.domain.models import Localidade, Preco, ViagemNormalizada
from app.normalizacao.interface import NormalizadorViagem
from app.domain.validacoes import (
    validar_ordem_datas,
    validar_duracao,
    validar_preco,
    validar_assentos,
)


class NormalizadorRota(NormalizadorViagem):

    def reconhece(self, payload: dict) -> bool:
        campos_identificadores = {
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
        }

        return campos_identificadores.issubset(payload.keys())

    def normalizar(self, payload: dict) -> ViagemNormalizada:
        partida = datetime.fromisoformat(
            payload["partida_em"]
        )

        chegada = datetime.fromisoformat(
            payload["chegada_em"]
        )

        validar_ordem_datas(
            partida,
            chegada,
        )

        duracao_minutos = int(
            payload["duracao_minutos"]
        )

        validar_duracao(
            partida,
            chegada,
            duracao_minutos,
        )

        valor = (
            payload["tarifa_centavos"] / 100
        )

        validar_preco(valor)

        assentos = int(
            payload["vagas"]
        )

        validar_assentos(assentos)

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

            categoria=payload[
                "classe"
            ].lower(),

            assentos_disponiveis=assentos,
        )