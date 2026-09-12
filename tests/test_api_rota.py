from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_normalizar_viagem_rota():
    payload = [
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
                "id_viagem": "ROT-2026-872",
                "empresa": "Rota Transportes",
                "origem": {
                    "cidade": "Paulo Afonso",
                    "uf": "BA",
                },
                "destino": {
                    "cidade": "Aracaju",
                    "uf": "SE",
                },
                "partida": "2026-10-15T07:00:00-03:00",
                "chegada": "2026-10-15T12:10:00-03:00",
                "duracao_minutos": 310,
                "preco": {
                    "valor": 89.9,
                    "moeda": "BRL",
                },
                "categoria": "convencional",
                "assentos_disponiveis": 22,
            }
        ],
    }


def test_rota_rejeita_chegada_anterior_partida():
    payload = [
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
            "empresa_identificada": "Rota Transportes",
            "campo": "chegada_em",
            "mensagem": (
                "A data de chegada deve ser posterior "
                "à data de saída."
            ),
        }
    }