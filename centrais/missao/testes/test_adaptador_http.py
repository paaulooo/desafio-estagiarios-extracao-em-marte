from __future__ import annotations

from unittest.mock import MagicMock

import pytest
import requests

from centrais.missao.adaptador_http import ClienteHttp


def _sessao_fake() -> MagicMock:
    sessao = MagicMock()
    sessao.request.return_value.json.return_value = {"ok": True}
    return sessao


def test_chamar_monta_url_com_base_url_e_rota():
    sessao = _sessao_fake()
    cliente = ClienteHttp(base_url="http://mundo-fake", sessao=sessao)

    resultado = cliente.chamar("GET", "/missao/estado")

    sessao.request.assert_called_once_with("GET", "http://mundo-fake/missao/estado", json=None)
    assert resultado == {"ok": True}


def test_chamar_repassa_payload_json():
    sessao = _sessao_fake()
    cliente = ClienteHttp(base_url="http://mundo-fake", sessao=sessao)

    cliente.chamar("POST", "/missao/registrar-webhook", json={"url": "http://a"})

    sessao.request.assert_called_once_with(
        "POST", "http://mundo-fake/missao/registrar-webhook", json={"url": "http://a"},
    )


def test_chamar_levanta_erro_em_resposta_de_falha():
    sessao = _sessao_fake()
    sessao.request.return_value.raise_for_status.side_effect = requests.HTTPError("400")
    cliente = ClienteHttp(base_url="http://mundo-fake", sessao=sessao)

    with pytest.raises(requests.HTTPError):
        cliente.chamar("POST", "/missao/autorizar-missao", json={})


def test_base_url_padrao_e_localhost_8000():
    cliente = ClienteHttp()

    assert cliente._base_url == "http://localhost:8000"
