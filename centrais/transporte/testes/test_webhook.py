from __future__ import annotations

from fastapi.testclient import TestClient

from centrais.transporte.webhook import webhook


def test_extracao_concluida_aciona_tratar_carga_nova(monkeypatch):
    chamadas = []
    monkeypatch.setattr(webhook, "tratar_carga_nova", lambda carga: chamadas.append(carga))
    cliente = TestClient(webhook.app)

    resposta = cliente.post("/webhooks/transporte", json={
        "identificador": "evt-1", "tipo": "extracao_concluida", "ciclo": 10,
        "dados": {"carga": "carga-1"},
    })

    assert resposta.status_code == 200
    assert chamadas == ["carga-1"]


def test_carga_disponivel_tambem_aciona_tratar_carga_nova(monkeypatch):
    chamadas = []
    monkeypatch.setattr(webhook, "tratar_carga_nova", lambda carga: chamadas.append(carga))
    cliente = TestClient(webhook.app)

    cliente.post("/webhooks/transporte", json={
        "identificador": "evt-2", "tipo": "carga_disponivel", "ciclo": 12,
        "dados": {"carga": "carga-2"},
    })

    assert chamadas == ["carga-2"]


def test_transporte_concluido_aciona_liberar_unidade(monkeypatch):
    chamadas = []
    monkeypatch.setattr(
        webhook, "liberar_unidade", lambda unidade, carga: chamadas.append((unidade, carga)),
    )
    cliente = TestClient(webhook.app)

    cliente.post("/webhooks/transporte", json={
        "identificador": "evt-3", "tipo": "transporte_concluido", "ciclo": 20,
        "dados": {"unidade": "transportadora-1", "carga": "carga-1", "modo": "normal"},
    })

    assert chamadas == [("transportadora-1", "carga-1")]


def test_viagem_abortada_aciona_reavaliar_carga(monkeypatch):
    chamadas = []
    monkeypatch.setattr(
        webhook, "reavaliar_carga", lambda carga, unidade: chamadas.append((carga, unidade)),
    )
    cliente = TestClient(webhook.app)

    cliente.post("/webhooks/transporte", json={
        "identificador": "evt-4", "tipo": "viagem_abortada", "ciclo": 25,
        "dados": {"unidade": "transportadora-1", "carga": "carga-1"},
    })

    assert chamadas == [("carga-1", "transportadora-1")]


def test_tipo_desconhecido_nao_quebra_a_rota():
    cliente = TestClient(webhook.app)

    resposta = cliente.post("/webhooks/transporte", json={
        "identificador": "evt-5", "tipo": "algo_nao_mapeado", "ciclo": 30,
        "dados": {},
    })

    assert resposta.status_code == 200
    assert resposta.json() == {"ok": True}
