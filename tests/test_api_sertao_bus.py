from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_normalizar_viagem_sertao_bus():
    payload = [
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
                "id_viagem": "SER-2026-100",
                "empresa": "Sertão Bus",
                "origem": {
                    "cidade": "Paulo Afonso",
                    "uf": "BA",
                },
                "destino": {
                    "cidade": "Maceió",
                    "uf": "AL",
                },
                "partida": "2026-10-16T08:00:00-03:00",
                "chegada": "2026-10-16T13:30:00-03:00",
                "duracao_minutos": 330,
                "preco": {
                    "valor": 105.9,
                    "moeda": "BRL",
                },
                "categoria": "executivo",
                "assentos_disponiveis": 14,
            }
        ],
    }


def test_sertao_bus_rejeita_assentos_negativos():
    payload = [
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
            "lugares_livres": -1,
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
            "empresa_identificada": "Sertão Bus",
            "campo": "lugares_livres",
            "mensagem": (
                "A quantidade de assentos disponíveis "
                "não pode ser negativa."
            ),
        }
    }