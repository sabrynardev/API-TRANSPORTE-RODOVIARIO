from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_rejeita_requisicao_inteira_quando_item_intermediario_e_invalido():
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
            "chegada_em": "2026-10-15T06:00:00-03:00",
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
    ]

    response = client.post(
        "/api/v1/viagens/normalizar",
        json=payload,
    )

    assert response.status_code == 422

    assert response.json() == {
        "detail": {
            "indice": 1,
            "empresa_identificada": "Rota Transportes",
            "campo": "chegada_em",
            "mensagem": (
                "A data de chegada deve ser posterior "
                "à data de saída."
            ),
        }
    }

    assert "viagens" not in response.json()
    assert "total" not in response.json()