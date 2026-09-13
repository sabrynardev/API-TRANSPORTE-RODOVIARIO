from datetime import datetime

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


class NormalizadorRota(NormalizadorViagem):

    def reconhece(self, payload: dict) -> bool:
        return "trip_id" in payload

    def normalizar(
        self,
        payload: dict,
    ) -> ViagemNormalizada:

        empresa = "Rota Transportes"

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
            raise ErroNormalizacao(
                mensagem="Campo obrigatório ausente.",
                campo=erro.args[0],
                empresa_identificada=empresa,
            )

        try:
            partida = datetime.fromisoformat(
                payload["partida_em"]
            )

            partida = aplicar_fuso_padrao(
                partida
            )

        except (ValueError, TypeError):
            raise ErroNormalizacao(
                mensagem="Data de saída inválida.",
                campo="partida_em",
                empresa_identificada=empresa,
            )

        try:
            chegada = datetime.fromisoformat(
                payload["chegada_em"]
            )

            chegada = aplicar_fuso_padrao(
                chegada
            )

        except (ValueError, TypeError):
            raise ErroNormalizacao(
                mensagem="Data de chegada inválida.",
                campo="chegada_em",
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
                campo="chegada_em",
                empresa_identificada=empresa,
            )

        try:
            duracao_minutos = int(
                payload["duracao_minutos"]
            )

        except (ValueError, TypeError):
            raise ErroNormalizacao(
                mensagem="Duração inválida.",
                campo="duracao_minutos",
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
                campo="duracao_minutos",
                empresa_identificada=empresa,
            )

        try:
            valor = (
                payload["tarifa_centavos"]
                / 100
            )

            validar_preco(valor)

        except (ValueError, TypeError) as erro:
            mensagem = str(erro)

            if not mensagem:
                mensagem = "Preço inválido."

            raise ErroNormalizacao(
                mensagem=mensagem,
                campo="tarifa_centavos",
                empresa_identificada=empresa,
            )

        try:
            assentos = int(
                payload["vagas"]
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
                campo="vagas",
                empresa_identificada=empresa,
            )

        try:
            categoria = (
                payload["classe"]
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
                campo="classe",
                empresa_identificada=empresa,
            )

        try:
            cidade_origem = (
                payload["origem"]["municipio"]
            )

            uf_origem = (
                payload["origem"]["estado"]
            )

            cidade_destino = (
                payload["destino"]["municipio"]
            )

            uf_destino = (
                payload["destino"]["estado"]
            )

        except (KeyError, TypeError):
            raise ErroNormalizacao(
                mensagem="Campo obrigatório ausente.",
                campo="origem/destino",
                empresa_identificada=empresa,
            )

        try:
            validar_uf(uf_origem)

        except ValueError as erro:
            raise ErroNormalizacao(
                mensagem=str(erro),
                campo="origem.estado",
                empresa_identificada=empresa,
            )

        try:
            validar_uf(uf_destino)

        except ValueError as erro:
            raise ErroNormalizacao(
                mensagem=str(erro),
                campo="destino.estado",
                empresa_identificada=empresa,
            )

        return ViagemNormalizada(
            id_viagem=payload["trip_id"],
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
                moeda=payload["moeda"],
            ),
            categoria=categoria,
            assentos_disponiveis=assentos,
        )