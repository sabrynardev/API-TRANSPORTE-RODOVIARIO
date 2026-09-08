from datetime import datetime

from app.domain.models import Localidade, Preco, ViagemNormalizada
from app.normalizacao.interface import NormalizadorViagem
from app.domain.validacoes import (
    validar_ordem_datas,
    validar_duracao,
    validar_preco,
    validar_assentos,
    validar_categoria,
)


class NormalizadorSertaoBus(NormalizadorViagem):

    def reconhece(self, payload: dict) -> bool:
        campos_identificadores = {
            "numero",
            "rota",
            "horarios",
            "duracao_horas",
            "preco_total",
            "moeda",
            "servico",
            "lugares_livres",
        }

        return campos_identificadores.issubset(payload.keys())

    def normalizar(self, payload: dict) -> ViagemNormalizada:
        origem_cidade, origem_uf = (
            payload["rota"]["partida"].rsplit(
                "/",
                1
            )
        )

        destino_cidade, destino_uf = (
            payload["rota"]["chegada"].rsplit(
                "/",
                1
            )
        )

        partida = datetime.fromisoformat(
            payload["horarios"]["saida"]
        )

        chegada = datetime.fromisoformat(
            payload["horarios"]["chegada"]
        )

        validar_ordem_datas(
            partida,
            chegada,
        )

        duracao_minutos = int(
            float(
                payload["duracao_horas"]
            ) * 60
        )

        validar_duracao(
            partida,
            chegada,
            duracao_minutos,
        )

        valor = float(
            payload["preco_total"]
        )

        validar_preco(valor)

        assentos = int(
            payload["lugares_livres"]
        )

        validar_assentos(assentos)

        categorias = {
            "CONV": "convencional",
            "EXEC": "executivo",
            "SEMI": "semileito",
            "LEITO": "leito",
        }

        categoria = categorias[
            payload["servico"]
        ]

        validar_categoria(categoria)

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