from abc import ABC, abstractmethod

from app.domain.models import ViagemNormalizada


class NormalizadorViagem(ABC):

    @abstractmethod
    def reconhece(self, payload: dict) -> bool:
        pass

    @abstractmethod
    def normalizar(self, payload: dict) -> ViagemNormalizada:
        pass