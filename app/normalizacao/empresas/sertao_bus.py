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


class NormalizadorSertaoBus(NormalizadorViagem):

    def reconhece(self, payload: dict) -> bool:
        return "numero" in payload

    def normalizar(
        self,
        payload: dict,
    ) -> ViagemNormalizada:

        empresa = "Sertão Bus"

        campos_obrigatorios = [
            "numero",
            "rota",
            "horarios",
            "duracao_horas",
            "preco_total",
            "moeda",
            "servico",
            "lugares_livres",
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
            cidade_origem, uf_origem = (
                payload["rota"]["partida"]
                .rsplit("/", 1)
            )

            cidade_destino, uf_destino = (
                payload["rota"]["chegada"]
                .rsplit("/", 1)
            )

        except (
            ValueError,
            TypeError,
            AttributeError,
            KeyError,
        ):
            raise ErroNormalizacao(
                mensagem="Formato de rota inválido.",
                campo="rota",
                empresa_identificada=empresa,
            )

        try:
            validar_uf(uf_origem)

        except ValueError as erro:
            raise ErroNormalizacao(
                mensagem=str(erro),
                campo="rota.partida",
                empresa_identificada=empresa,
            )

        try:
            validar_uf(uf_destino)

        except ValueError as erro:
            raise ErroNormalizacao(
                mensagem=str(erro),
                campo="rota.chegada",
                empresa_identificada=empresa,
            )

        try:
            partida = datetime.fromisoformat(
                payload["horarios"]["saida"]
            )

            partida = aplicar_fuso_padrao(
                partida
            )

        except (
            ValueError,
            TypeError,
            KeyError,
        ):
            raise ErroNormalizacao(
                mensagem="Data de saída inválida.",
                campo="horarios.saida",
                empresa_identificada=empresa,
            )

        try:
            chegada = datetime.fromisoformat(
                payload["horarios"]["chegada"]
            )

            chegada = aplicar_fuso_padrao(
                chegada
            )

        except (
            ValueError,
            TypeError,
            KeyError,
        ):
            raise ErroNormalizacao(
                mensagem="Data de chegada inválida.",
                campo="horarios.chegada",
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
                campo="horarios.chegada",
                empresa_identificada=empresa,
            )

        try:
            duracao_minutos = int(
                float(
                    payload["duracao_horas"]
                )
                * 60
            )

        except (ValueError, TypeError):
            raise ErroNormalizacao(
                mensagem="Duração inválida.",
                campo="duracao_horas",
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
                campo="duracao_horas",
                empresa_identificada=empresa,
            )

        try:
            valor = float(
                payload["preco_total"]
            )

            validar_preco(valor)

        except (ValueError, TypeError) as erro:
            mensagem = str(erro)

            if not mensagem:
                mensagem = "Preço inválido."

            raise ErroNormalizacao(
                mensagem=mensagem,
                campo="preco_total",
                empresa_identificada=empresa,
            )

        try:
            assentos = int(
                payload["lugares_livres"]
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
                campo="lugares_livres",
                empresa_identificada=empresa,
            )

        categorias = {
            "CONV": "convencional",
            "EXEC": "executivo",
            "SEMI": "semileito",
            "LEITO": "leito",
        }

        categoria = categorias.get(
            payload["servico"]
        )

        try:
            validar_categoria(categoria)

        except ValueError as erro:
            raise ErroNormalizacao(
                mensagem=str(erro),
                campo="servico",
                empresa_identificada=empresa,
            )

        return ViagemNormalizada(
            id_viagem=payload["numero"],
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