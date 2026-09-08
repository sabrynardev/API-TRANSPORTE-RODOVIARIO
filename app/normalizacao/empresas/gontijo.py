from datetime import datetime
from zoneinfo import ZoneInfo

from app.domain.models import Localidade, Preco, ViagemNormalizada
from app.normalizacao.interface import NormalizadorViagem


class NormalizadorGontijo(NormalizadorViagem):

    def reconhece(self, payload: dict) -> bool:
        campos_identificadores = {
            "serviceCode",
            "from",
            "to",
            "departure",
            "arrival",
            "estimatedDurationSeconds",
            "fare",
            "serviceClass",
            "availableSeats",
        }

        return campos_identificadores.issubset(payload.keys())

    def normalizar(self, payload: dict) -> ViagemNormalizada:
        fuso_bahia = ZoneInfo("America/Bahia")

        partida = datetime.fromisoformat(
            payload["departure"].replace("Z", "+00:00")
        ).astimezone(fuso_bahia)

        chegada = datetime.fromisoformat(
            payload["arrival"].replace("Z", "+00:00")
        ).astimezone(fuso_bahia)

        duracao_minutos = (
            int(payload["estimatedDurationSeconds"]) // 60
        )

        categorias = {
            "CONVENTIONAL": "convencional",
            "EXECUTIVE": "executivo",
            "SEMI_SLEEPER": "semileito",
            "SLEEPER": "leito",
        }

        categoria = categorias[payload["serviceClass"]]

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
                valor=float(payload["fare"]["amount"]),
                moeda=payload["fare"]["currency"],
            ),

            categoria=categoria,

            assentos_disponiveis=int(
                payload["availableSeats"]
            ),
        )