from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_rejeita_formato_desconhecido():
    payload = [
        {
            "qualquer_coisa": "teste",
            "banana": 123,
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
            "empresa_identificada": None,
            "campo": None,
            "mensagem": (
                "O formato do payload não corresponde "
                "a nenhuma companhia suportada."
            ),
        }
    }


def test_rejeita_campo_obrigatorio_ausente():
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
            "campo": "vagas",
            "mensagem": "Campo obrigatório ausente.",
        }
    }


def test_rejeita_preco_invalido():
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
            "tarifa_centavos": 0,
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
            "campo": "tarifa_centavos",
            "mensagem": "O preço deve ser maior que zero.",
        }
    }


def test_rejeita_duracao_incompativel():
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
            "duracao_minutos": 100,
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
            "campo": "duracao_minutos",
            "mensagem": (
                "A duração informada é incompatível "
                "com os horários de partida e chegada."
            ),
        }
    }

def test_rejeita_uf_com_tamanho_invalido():
    payload = [
        {
            "trip_id": "ROT-2026-872",
            "origem": {
                "municipio": "Paulo Afonso",
                "estado": "BAH",
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

    assert response.status_code == 422

    assert response.json() == {
        "detail": {
            "indice": 0,
            "empresa_identificada": "Rota Transportes",
            "campo": "origem.estado",
            "mensagem": "A UF deve possuir exatamente 2 caracteres.",
        }
    }

def test_rejeita_data_invalida():
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
            "partida_em": "DATA-INVALIDA",
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

    assert response.status_code == 422
    assert response.json()["detail"]["campo"] == "partida_em"
    assert (
        response.json()["detail"]["empresa_identificada"]
        == "Rota Transportes"
    )


def test_rejeita_duracao_zero():
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
            "duracao_minutos": 0,
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

    assert response.json()["detail"] == {
        "indice": 0,
        "empresa_identificada": "Rota Transportes",
        "campo": "duracao_minutos",
        "mensagem": "A duração deve ser maior que zero.",
    }


def test_aceita_zero_assentos():
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
            "vagas": 0,
        }
    ]

    response = client.post(
        "/api/v1/viagens/normalizar",
        json=payload,
    )

    assert response.status_code == 200
    assert (
        response.json()["viagens"][0]["assentos_disponiveis"]
        == 0
    )


def test_ignora_campo_extra():
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
            "campo_que_nao_interessa": "IGNORAR",
        }
    ]

    response = client.post(
        "/api/v1/viagens/normalizar",
        json=payload,
    )

    assert response.status_code == 200

    viagem = response.json()["viagens"][0]

    assert "campo_que_nao_interessa" not in viagem

def test_rejeita_campo_aninhado_ausente():
    payload = [
        {
            "trip_id": "ROT-2026-872",
            "origem": {
                "municipio": "Paulo Afonso"
                # "estado" ausente
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

    assert response.status_code == 422
    assert (
        response.json()["detail"]["empresa_identificada"]
        == "Rota Transportes"
    )


def test_aplica_fuso_bahia_quando_data_nao_possui_fuso():
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
            "partida_em": "2026-10-15T07:00:00",
            "chegada_em": "2026-10-15T12:10:00",
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

    viagem = response.json()["viagens"][0]

    assert viagem["partida"] == (
        "2026-10-15T07:00:00-03:00"
    )

    assert viagem["chegada"] == (
        "2026-10-15T12:10:00-03:00"
    )