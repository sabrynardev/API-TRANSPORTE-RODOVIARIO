from pydantic import BaseModel


class Localidade(BaseModel):
    cidade: str
    uf: str


class Preco(BaseModel):
    valor: float
    moeda: str


class ViagemNormalizada(BaseModel):
    id_viagem: str
    empresa: str
    origem: Localidade
    destino: Localidade
    partida: str
    chegada: str
    duracao_minutos: int
    preco: Preco
    categoria: str
    assentos_disponiveis: int


class RespostaNormalizacao(BaseModel):
    total: int
    viagens: list[ViagemNormalizada]