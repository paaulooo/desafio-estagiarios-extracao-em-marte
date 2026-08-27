from __future__ import annotations

from unittest.mock import MagicMock

from centrais.transporte.transporte_client import ClienteDeMissao, ClienteDeTransporte


def _sessao_fake() -> MagicMock:
    sessao = MagicMock()
    sessao.get.return_value.json.return_value = []
    sessao.post.return_value.json.return_value = {}
    return sessao


def test_consultar_rotas_chama_endpoint_correto():
    sessao = _sessao_fake()
    sessao.get.return_value.json.return_value = [{"identificador": "rota-1"}]
    cliente = ClienteDeTransporte(base_url="http://mundo-fake", sessao=sessao)

    resultado = cliente.consultar_rotas()

    sessao.get.assert_called_once_with("http://mundo-fake/transporte/rotas")
    assert resultado == [{"identificador": "rota-1"}]


def test_planejar_transporte_envia_identificador_como_query_param():
    sessao = _sessao_fake()
    sessao.get.return_value.json.return_value = {"carga": "carga-1", "rotas_disponiveis": ["rota-1"]}
    cliente = ClienteDeTransporte(base_url="http://mundo-fake", sessao=sessao)

    resultado = cliente.planejar_transporte("carga-1")

    sessao.get.assert_called_once_with(
        "http://mundo-fake/transporte/planejar-transporte",
        params={"identificador_da_carga": "carga-1"},
    )
    assert resultado == {"carga": "carga-1", "rotas_disponiveis": ["rota-1"]}


def test_carregar_monta_payload_correto():
    sessao = _sessao_fake()
    sessao.post.return_value.json.return_value = {"aceito": True}
    cliente = ClienteDeTransporte(base_url="http://mundo-fake", sessao=sessao)

    resposta = cliente.carregar("transportadora-1", "carga-1")

    sessao.post.assert_called_once_with("http://mundo-fake/transporte/carregar", json={
        "identificador_da_unidade": "transportadora-1",
        "identificador_da_carga": "carga-1",
    })
    assert resposta == {"aceito": True}


def test_iniciar_viagem_monta_payload_com_modo_default_normal():
    sessao = _sessao_fake()
    sessao.post.return_value.json.return_value = {"aceito": True}
    cliente = ClienteDeTransporte(base_url="http://mundo-fake", sessao=sessao)

    cliente.iniciar_viagem("transportadora-1", "rota-1", "carga-1", "aut-123")

    sessao.post.assert_called_once_with("http://mundo-fake/transporte/iniciar-viagem", json={
        "identificador_da_unidade": "transportadora-1",
        "identificador_da_rota": "rota-1",
        "identificador_da_carga": "carga-1",
        "id_autorizacao": "aut-123",
        "modo": "normal",
    })


def test_iniciar_viagem_aceita_modo_explicito():
    sessao = _sessao_fake()
    cliente = ClienteDeTransporte(base_url="http://mundo-fake", sessao=sessao)

    cliente.iniciar_viagem("transportadora-1", "rota-1", "carga-1", "aut-123", modo="rapido")

    payload_enviado = sessao.post.call_args.kwargs["json"]
    assert payload_enviado["modo"] == "rapido"


def test_descarregar_e_retornar_unidade_chamam_endpoints_corretos():
    sessao = _sessao_fake()
    cliente = ClienteDeTransporte(base_url="http://mundo-fake", sessao=sessao)

    cliente.descarregar("transportadora-1", "carga-1")
    cliente.retornar_unidade("transportadora-1")

    sessao.post.assert_any_call("http://mundo-fake/transporte/descarregar", json={
        "identificador_da_unidade": "transportadora-1",
        "identificador_da_carga": "carga-1",
    })
    sessao.post.assert_any_call("http://mundo-fake/transporte/retornar-unidade", json={
        "identificador_da_unidade": "transportadora-1",
    })


def test_autorizar_missao_usa_classe_rapida_por_padrao():
    sessao = _sessao_fake()
    sessao.post.return_value.json.return_value = {"id_autorizacao": "aut-1"}
    missao = ClienteDeMissao(base_url="http://mundo-fake", sessao=sessao)

    resultado = missao.autorizar_missao(operacao="iniciar_viagem", central_solicitante="transporte")

    sessao.post.assert_called_once_with("http://mundo-fake/missao/autorizar-missao", json={
        "operacao": "iniciar_viagem",
        "central_solicitante": "transporte",
        "classe": "rapida",
    })
    assert resultado == {"id_autorizacao": "aut-1"}


def test_registrar_webhook_envia_url():
    sessao = _sessao_fake()
    missao = ClienteDeMissao(base_url="http://mundo-fake", sessao=sessao)

    missao.registrar_webhook("http://minha-central/webhooks/transporte")

    sessao.post.assert_called_once_with("http://mundo-fake/missao/registrar-webhook", json={
        "url": "http://minha-central/webhooks/transporte",
    })
