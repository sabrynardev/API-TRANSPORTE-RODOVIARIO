from datetime import datetime
from zoneinfo import ZoneInfo

from app.domain.exceptions import ErroNormalizacao
from app.domain.models import (
    Localidade,
    Preco,
    ViagemNormalizada,
)
from app.domain.validacoes import (
    validar_assentos,
    validar_campos_obrigatorios,
    validar_categoria,
    validar_duracao,
    validar_ordem_datas,
    validar_preco,
    validar_uf,
)
from app.normalizacao.interface import NormalizadorViagem


class NormalizadorProgresso(NormalizadorViagem):

    def reconhece(self, payload: dict) -> bool:
        return "codigoViagem" in payload

    def normalizar(
        self,
        payload: dict,
    ) -> ViagemNormalizada:

        empresa = "Auto Viação Progresso"

        campos_obrigatorios = [
            "codigoViagem",
            "cidadeOrigem",
            "ufOrigem",
            "cidadeDestino",
            "ufDestino",
            "dataHoraSaida",
            "dataHoraChegada",
            "tempoEstimado",
            "valorPassagem",
            "tipoServico",
            "assentosDisponiveis",
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

        fuso = ZoneInfo(
            payload.get(
                "fusoHorario",
                "America/Bahia",
            )
        )

        try:
            partida = datetime.strptime(
                payload["dataHoraSaida"],
                "%d/%m/%Y %H:%M",
            ).replace(tzinfo=fuso)

        except (ValueError, TypeError):
            raise ErroNormalizacao(
                mensagem="Data de saída inválida.",
                campo="dataHoraSaida",
                empresa_identificada=empresa,
            )

        try:
            chegada = datetime.strptime(
                payload["dataHoraChegada"],
                "%d/%m/%Y %H:%M",
            ).replace(tzinfo=fuso)

        except (ValueError, TypeError):
            raise ErroNormalizacao(
                mensagem="Data de chegada inválida.",
                campo="dataHoraChegada",
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
                campo="dataHoraChegada",
                empresa_identificada=empresa,
            )

        try:
            horas, minutos = map(
                int,
                payload["tempoEstimado"].split(":"),
            )

            duracao_minutos = (
                horas * 60
                + minutos
            )

        except (ValueError, TypeError, AttributeError):
            raise ErroNormalizacao(
                mensagem="Duração inválida.",
                campo="tempoEstimado",
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
                campo="tempoEstimado",
                empresa_identificada=empresa,
            )

        try:
            valor = float(
                str(
                    payload["valorPassagem"]
                ).replace(",", ".")
            )

            validar_preco(valor)

        except (ValueError, TypeError) as erro:
            mensagem = str(erro)

            if not mensagem:
                mensagem = "Preço inválido."

            raise ErroNormalizacao(
                mensagem=mensagem,
                campo="valorPassagem",
                empresa_identificada=empresa,
            )

        try:
            assentos = int(
                payload["assentosDisponiveis"]
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
                campo="assentosDisponiveis",
                empresa_identificada=empresa,
            )

        try:
            categoria = (
                payload["tipoServico"]
                .lower()
            )

            validar_categoria(categoria)

        except (ValueError, AttributeError) as erro:
            mensagem = str(erro)

            if not mensagem:
                mensagem = (
                    "A categoria informada "
                    "não pode ser normalizada."
                )

            raise ErroNormalizacao(
                mensagem=mensagem,
                campo="tipoServico",
                empresa_identificada=empresa,
            )

        uf_origem = payload["ufOrigem"]
        uf_destino = payload["ufDestino"]

        try:
            validar_uf(uf_origem)

        except ValueError as erro:
            raise ErroNormalizacao(
                mensagem=str(erro),
                campo="ufOrigem",
                empresa_identificada=empresa,
            )

        try:
            validar_uf(uf_destino)

        except ValueError as erro:
            raise ErroNormalizacao(
                mensagem=str(erro),
                campo="ufDestino",
                empresa_identificada=empresa,
            )

        return ViagemNormalizada(
            id_viagem=payload["codigoViagem"],
            empresa=empresa,
            origem=Localidade(
                cidade=payload["cidadeOrigem"],
                uf=uf_origem,
            ),
            destino=Localidade(
                cidade=payload["cidadeDestino"],
                uf=uf_destino,
            ),
            partida=partida.isoformat(),
            chegada=chegada.isoformat(),
            duracao_minutos=duracao_minutos,
            preco=Preco(
                valor=valor,
                moeda="BRL",
            ),
            categoria=categoria,
            assentos_disponiveis=assentos,
        )