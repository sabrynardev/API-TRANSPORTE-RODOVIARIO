from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_normalizar_viagem_gontijo():
    payload = [
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
        }
    ]

    response = client.post(
        "/api/v1/viagens/normalizar",
        json=payload,
    )

    assert response.status_code == 200

    assert response.json() == {
        "total": 1,
        "viagens": [
            {
                "id_viagem": "GON-2026-554",
                "empresa": "Gontijo",
                "origem": {
                    "cidade": "Paulo Afonso",
                    "uf": "BA",
                },
                "destino": {
                    "cidade": "Belo Horizonte",
                    "uf": "MG",
                },
                "partida": "2026-10-15T16:30:00-03:00",
                "chegada": "2026-10-16T09:10:00-03:00",
                "duracao_minutos": 1000,
                "preco": {
                    "valor": 289.5,
                    "moeda": "BRL",
                },
                "categoria": "semileito",
                "assentos_disponiveis": 9,
            }
        ],
    }


def test_gontijo_rejeita_categoria_desconhecida():
    payload = [
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
            "serviceClass": "PREMIUM",
            "availableSeats": 9,
        }
    ]

    response = client.post(
        "/api/v1/viagens/normalizar",
        json=payload,
    )

    assert response.status_code == 422

    assert response.json() == {
        "detail": {
            "indice": 0,
            "empresa_identificada": "Gontijo",
            "campo": "serviceClass",
            "mensagem": (
                "A categoria informada não pode ser normalizada."
            ),
        }
    }