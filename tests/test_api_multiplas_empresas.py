from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_normalizar_multiplas_empresas_preserva_ordem():
    payload = [
        {
            "codigoViagem": "PRG-2026-001",
            "cidadeOrigem": "Paulo Afonso",
            "ufOrigem": "BA",
            "cidadeDestino": "Recife",
            "ufDestino": "PE",
            "dataHoraSaida": "15/10/2026 06:30",
            "dataHoraChegada": "15/10/2026 12:50",
            "fusoHorario": "America/Bahia",
            "tempoEstimado": "06:20",
            "valorPassagem": "129,90",
            "tipoServico": "EXECUTIVO",
            "assentosDisponiveis": "18",
        },
        {
            "trip_id": "ROT-2026-872",
            "origem": {
                "municipio": "Paulo Afonso",
                "estado": "BA",
            },
            "destino": {
                "municipio": "Aracaju",
                "estado": "SE",
            },
            "partida_em": "2026-10-15T07:00:00-03:00",
            "chegada_em": "2026-10-15T12:10:00-03:00",
            "duracao_minutos": 310,
            "tarifa_centavos": 8990,
            "moeda": "BRL",
            "classe": "convencional",
            "vagas": 22,
        },
        {
            "serviceCode": "GON-2026-554",
            "from": {
                "city": "Paulo Afonso",
                "state": "BA",
            },
            "to": {
                "city": "Belo Horizonte",
                "state": "MG",
            },
            "departure": "2026-10-15T19:30:00Z",
            "arrival": "2026-10-16T12:10:00Z",
            "estimatedDurationSeconds": 60000,
            "fare": {
                "amount": "289.50",
                "currency": "BRL",
            },
            "serviceClass": "SEMI_SLEEPER",
            "availableSeats": 9,
        },
        {
            "numero": "SER-2026-100",
            "rota": {
                "partida": "Paulo Afonso/BA",
                "chegada": "Maceió/AL",
            },
            "horarios": {
                "saida": "2026-10-16T08:00:00-03:00",
                "chegada": "2026-10-16T13:30:00-03:00",
            },
            "duracao_horas": 5.5,
            "preco_total": 105.90,
            "moeda": "BRL",
            "servico": "EXEC",
            "lugares_livres": 14,
        },
    ]

    response = client.post(
        "/api/v1/viagens/normalizar",
        json=payload,
    )

    assert response.status_code == 200

    resposta = response.json()

    assert resposta["total"] == 4

    assert [
        viagem["empresa"]
        for viagem in resposta["viagens"]
    ] == [
        "Auto Viação Progresso",
        "Rota Transportes",
        "Gontijo",
        "Sertão Bus",
    ]

    assert [
        viagem["id_viagem"]
        for viagem in resposta["viagens"]
    ] == [
        "PRG-2026-001",
        "ROT-2026-872",
        "GON-2026-554",
        "SER-2026-100",
    ]