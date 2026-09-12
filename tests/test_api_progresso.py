from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_normalizar_viagem_progresso():
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
                "id_viagem": "PRG-2026-001",
                "empresa": "Auto Viação Progresso",
                "origem": {
                    "cidade": "Paulo Afonso",
                    "uf": "BA",
                },
                "destino": {
                    "cidade": "Recife",
                    "uf": "PE",
                },
                "partida": "2026-10-15T06:30:00-03:00",
                "chegada": "2026-10-15T12:50:00-03:00",
                "duracao_minutos": 380,
                "preco": {
                    "valor": 129.9,
                    "moeda": "BRL",
                },
                "categoria": "executivo",
                "assentos_disponiveis": 18,
            }
        ],
    }


def test_progresso_ignora_campos_extras():
    payload = [
        {
            "codigoViagem": "PRG-2026-002",
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
            "campo_extra": "deve ser ignorado",
            "observacao_interna": "não deve aparecer na resposta",
        }
    ]

    response = client.post(
        "/api/v1/viagens/normalizar",
        json=payload,
    )

    assert response.status_code == 200

    resposta = response.json()

    assert resposta["total"] == 1

    viagem = resposta["viagens"][0]

    assert viagem["id_viagem"] == "PRG-2026-002"
    assert viagem["empresa"] == "Auto Viação Progresso"

    assert "campo_extra" not in viagem
    assert "observacao_interna" not in viagem