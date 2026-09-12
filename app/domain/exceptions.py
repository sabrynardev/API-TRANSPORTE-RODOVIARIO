class ErroNormalizacao(Exception):
    def __init__(
        self,
        mensagem: str,
        campo: str | None = None,
        empresa_identificada: str | None = None,
    ):
        self.mensagem = mensagem
        self.campo = campo
        self.empresa_identificada = empresa_identificada

        super().__init__(mensagem)