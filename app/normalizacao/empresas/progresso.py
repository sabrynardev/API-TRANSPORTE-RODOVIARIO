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


class NormalizadorProgresso(NormalizadorViagem):

    def reconhece(self, payload: dict) -> bool:
        return "codigoViagem" in payload

    def normalizar(self, payload: dict) -> ViagemNormalizada:
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
            campo = erro.args[0]

            raise ErroNormalizacao(
                mensagem="Campo obrigatório ausente.",
                campo=campo,
                empresa_identificada="Auto Viação Progresso",
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
        except ValueError:
            raise ErroNormalizacao(
                mensagem="A data de saída possui formato inválido.",
                campo="dataHoraSaida",
                empresa_identificada="Auto Viação Progresso",
            )

        try:
            chegada = datetime.strptime(
                payload["dataHoraChegada"],
                "%d/%m/%Y %H:%M",
            ).replace(tzinfo=fuso)
        except ValueError:
            raise ErroNormalizacao(
                mensagem="A data de chegada possui formato inválido.",
                campo="dataHoraChegada",
                empresa_identificada="Auto Viação Progresso",
            )

        try:
            validar_ordem_datas(partida, chegada)
        except ValueError as erro:
            raise ErroNormalizacao(
                mensagem=str(erro),
                campo="dataHoraChegada",
                empresa_identificada="Auto Viação Progresso",
            )

        try:
            horas, minutos = map(
                int,
                payload["tempoEstimado"].split(":"),
            )

            duracao_minutos = horas * 60 + minutos
        except (ValueError, AttributeError):
            raise ErroNormalizacao(
                mensagem="A duração informada é inválida.",
                campo="tempoEstimado",
                empresa_identificada="Auto Viação Progresso",
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
                empresa_identificada="Auto Viação Progresso",
            )

        try:
            valor = float(
                payload["valorPassagem"].replace(",", ".")
            )
        except (ValueError, AttributeError):
            raise ErroNormalizacao(
                mensagem="O preço informado é inválido.",
                campo="valorPassagem",
                empresa_identificada="Auto Viação Progresso",
            )

        try:
            validar_preco(valor)
        except ValueError as erro:
            raise ErroNormalizacao(
                mensagem=str(erro),
                campo="valorPassagem",
                empresa_identificada="Auto Viação Progresso",
            )

        try:
            assentos = int(
                payload["assentosDisponiveis"]
            )
        except (ValueError, TypeError):
            raise ErroNormalizacao(
                mensagem="A quantidade de assentos disponíveis é inválida.",
                campo="assentosDisponiveis",
                empresa_identificada="Auto Viação Progresso",
            )

        try:
            validar_assentos(assentos)
        except ValueError as erro:
            raise ErroNormalizacao(
                mensagem=str(erro),
                campo="assentosDisponiveis",
                empresa_identificada="Auto Viação Progresso",
            )

        try:
            categoria = payload["tipoServico"].lower()
        except AttributeError:
            raise ErroNormalizacao(
                mensagem="A categoria informada não pode ser normalizada.",
                campo="tipoServico",
                empresa_identificada="Auto Viação Progresso",
            )

        try:
            validar_categoria(categoria)
        except ValueError as erro:
            raise ErroNormalizacao(
                mensagem=str(erro),
                campo="tipoServico",
                empresa_identificada="Auto Viação Progresso",
            )

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
            categoria=categoria,
            assentos_disponiveis=assentos,
        )