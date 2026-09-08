from datetime import datetime

def validar_ordem_datas(
    partida: datetime,
    chegada: datetime,
) -> None:
    if chegada <= partida:
        raise ValueError(
            "A data de chegada deve ser posterior à data de saída."
        )