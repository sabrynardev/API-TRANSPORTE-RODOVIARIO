from datetime import datetime

def validar_ordem_datas(
    partida: datetime,
    chegada: datetime,
) -> None:
    if chegada <= partida:
        raise ValueError(
            "A data de chegada deve ser posterior à data de saída."
        )
    
def validar_duracao(
    partida: datetime,
    chegada: datetime,
    duracao_minutos: int,
) -> None:
    if duracao_minutos <= 0:
        raise ValueError(
            "A duração deve ser maior que zero."
        )

    duracao_calculada = int(
        (chegada - partida).total_seconds() / 60
    )

    if duracao_minutos != duracao_calculada:
        raise ValueError(
            "A duração informada é incompatível "
            "com os horários de partida e chegada."
        )