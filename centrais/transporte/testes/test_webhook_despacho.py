from __future__ import annotations

from unittest.mock import MagicMock

from centrais.transporte.webhook import webhook


def _cliente_fake(cargas=None, transportadores=None) -> MagicMock:
    cliente = MagicMock()
    cliente.consultar_cargas_disponiveis.return_value = cargas or []
    cliente.consultar_transportadores.return_value = transportadores or []
    return cliente


def test_tratar_carga_nova_despacha_quando_ha_unidade_disponivel(monkeypatch):
    carga = {"identificador": "carga-1", "mineral": "hematita", "quantidade": 10.0, "qualidade": None}
    cliente = _cliente_fake(
        cargas=[carga],
        transportadores=[{"identificador": "transportadora-1", "estado": "disponivel", "localizacao": "patio"}],
    )
    monkeypatch.setattr(webhook, "_cliente", cliente)
    despachos = []
    monkeypatch.setattr(
        webhook, "despachar_carga",
        lambda cli, missao, c, unidade, valor_por_kg: despachos.append((c, unidade, valor_por_kg)),
    )

    webhook.tratar_carga_nova("carga-1")

    assert despachos == [(carga, "transportadora-1", 5.0)]


def test_tratar_carga_nova_nao_faz_nada_sem_unidade_disponivel(monkeypatch):
    carga = {"identificador": "carga-1", "mineral": "hematita", "quantidade": 10.0, "qualidade": None}
    cliente = _cliente_fake(
        cargas=[carga],
        transportadores=[{"identificador": "transportadora-1", "estado": "executando", "localizacao": "patio"}],
    )
    monkeypatch.setattr(webhook, "_cliente", cliente)
    despachos = []
    monkeypatch.setattr(webhook, "despachar_carga", lambda *args: despachos.append(args))

    webhook.tratar_carga_nova("carga-1")

    assert despachos == []


def test_tratar_carga_nova_nao_faz_nada_se_carga_desconhecida(monkeypatch):
    cliente = _cliente_fake(
        cargas=[],
        transportadores=[{"identificador": "transportadora-1", "estado": "disponivel", "localizacao": "patio"}],
    )
    monkeypatch.setattr(webhook, "_cliente", cliente)
    despachos = []
    monkeypatch.setattr(webhook, "despachar_carga", lambda *args: despachos.append(args))

    webhook.tratar_carga_nova("carga-inexistente")

    assert despachos == []


def test_tratar_carga_nova_ignora_excecao_do_despacho(monkeypatch):
    carga = {"identificador": "carga-1", "mineral": "hematita", "quantidade": 10.0, "qualidade": None}
    cliente = _cliente_fake(
        cargas=[carga],
        transportadores=[{"identificador": "transportadora-1", "estado": "disponivel", "localizacao": "patio"}],
    )
    monkeypatch.setattr(webhook, "_cliente", cliente)

    def _explode(*args):
        raise ValueError("Não foi encontrada rota adequada para a carga.")

    monkeypatch.setattr(webhook, "despachar_carga", _explode)

    webhook.tratar_carga_nova("carga-1")  # não deve levantar


def test_liberar_unidade_descarrega_e_retorna_a_unidade(monkeypatch):
    cliente = MagicMock()
    monkeypatch.setattr(webhook, "_cliente", cliente)

    webhook.liberar_unidade("transportadora-1", "carga-1")

    cliente.descarregar.assert_called_once_with("transportadora-1", "carga-1")
    cliente.retornar_unidade.assert_called_once_with("transportadora-1")


def test_liberar_unidade_ignora_excecao_de_rede(monkeypatch):
    cliente = MagicMock()
    cliente.descarregar.side_effect = RuntimeError("falha de rede")
    monkeypatch.setattr(webhook, "_cliente", cliente)

    webhook.liberar_unidade("transportadora-1", "carga-1")  # não deve levantar


def test_reavaliar_carga_libera_a_unidade_e_tenta_redespachar(monkeypatch):
    carga = {"identificador": "carga-1", "mineral": "jarosita", "quantidade": 5.0, "qualidade": None}
    cliente = _cliente_fake(
        cargas=[carga],
        transportadores=[{"identificador": "transportadora-2", "estado": "disponivel", "localizacao": "patio"}],
    )
    monkeypatch.setattr(webhook, "_cliente", cliente)
    despachos = []
    monkeypatch.setattr(
        webhook, "despachar_carga",
        lambda cli, missao, c, unidade, valor_por_kg: despachos.append((c, unidade, valor_por_kg)),
    )

    webhook.reavaliar_carga("carga-1", "transportadora-1")

    cliente.retornar_unidade.assert_called_once_with("transportadora-1")
    assert despachos == [(carga, "transportadora-2", 35.0)]


def test_reavaliar_carga_tenta_redespachar_mesmo_se_retornar_unidade_falhar(monkeypatch):
    carga = {"identificador": "carga-1", "mineral": "hematita", "quantidade": 5.0, "qualidade": None}
    cliente = _cliente_fake(
        cargas=[carga],
        transportadores=[{"identificador": "transportadora-2", "estado": "disponivel", "localizacao": "patio"}],
    )
    cliente.retornar_unidade.side_effect = RuntimeError("falha de rede")
    monkeypatch.setattr(webhook, "_cliente", cliente)
    despachos = []
    monkeypatch.setattr(
        webhook, "despachar_carga",
        lambda cli, missao, c, unidade, valor_por_kg: despachos.append((c, unidade, valor_por_kg)),
    )

    webhook.reavaliar_carga("carga-1", "transportadora-1")  # não deve levantar

    assert despachos == [(carga, "transportadora-2", 5.0)]
