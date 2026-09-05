from app.normalizacao.interface import NormalizadorViagem

class NormalizadorRegistry:
    
    def __init__(self):
        self._normalizadores: list[NormalizadorViagem] = []

    def registrar(self, normalizador: NormalizadorViagem) -> None:
        self._normalizadores.append(normalizador)

    def resolver(self, payload: dict) -> NormalizadorViagem | None:
        for normalizador in self._normalizadores:
            if normalizador.reconhece(payload):
                return normalizador

        return None