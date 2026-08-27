from __future__ import annotations

from unittest.mock import MagicMock

from centrais.transporte.orquestrador import despachar_carga


def _cliente_fake_com_uma_rota() -> MagicMock:
    cliente = MagicMock()
    cliente.planejar_transporte.return_value = {"carga": "carga-1", "rotas_disponiveis": ["rota-1"]}
    cliente.consultar_rotas.return_value = [
        {"identificador": "rota-1", "custo_energia_base": 3.0, "multiplicador_degradacao": 1.0},
        {"identificador": "rota-2", "custo_energia_base": 3.0, "multiplicador_degradacao": 1.0},
    ]
    return cliente


def test_despachar_carga_filtra_rotas_pelo_planejamento():
    cliente = _cliente_fake_com_uma_rota()
    missao = MagicMock()
    missao.autorizar_missao.return_value = {"id_autorizacao": "aut-999"}
    carga = {"identificador": "carga-1", "quantidade": 10.0}

    despachar_carga(cliente, missao, carga, "transportadora-1", valor_por_kg=10.0)

    rota_escolhida = cliente.iniciar_viagem.call_args.args[1]
    assert rota_escolhida == "rota-1"  # rota-2 nunca foi liberada pelo planejamento


def test_despachar_carga_chama_carregar_antes_de_iniciar_viagem():
    cliente = _cliente_fake_com_uma_rota()
    missao = MagicMock()
    missao.autorizar_missao.return_value = {"id_autorizacao": "aut-999"}
    carga = {"identificador": "carga-1", "quantidade": 10.0}

    despachar_carga(cliente, missao, carga, "transportadora-1", valor_por_kg=10.0)

    ordem_das_chamadas = [chamada[0] for chamada in cliente.method_calls]
    assert ordem_das_chamadas.index("carregar") < ordem_das_chamadas.index("iniciar_viagem")


def test_despachar_carga_encadeia_autorizacao_no_iniciar_viagem():
    cliente = _cliente_fake_com_uma_rota()
    missao = MagicMock()
    missao.autorizar_missao.return_value = {"id_autorizacao": "aut-999"}
    carga = {"identificador": "carga-1", "quantidade": 10.0}

    despachar_carga(cliente, missao, carga, "transportadora-1", valor_por_kg=10.0)

    missao.autorizar_missao.assert_called_once_with(
        operacao="iniciar_viagem", central_solicitante="transporte",
    )
    assert "aut-999" in cliente.iniciar_viagem.call_args.args


def test_despachar_carga_repassa_unidade_e_carga_corretas():
    cliente = _cliente_fake_com_uma_rota()
    missao = MagicMock()
    missao.autorizar_missao.return_value = {"id_autorizacao": "aut-1"}
    carga = {"identificador": "carga-42", "quantidade": 7.0}

    despachar_carga(cliente, missao, carga, "transportadora-9", valor_por_kg=15.0)

    cliente.carregar.assert_called_once_with("transportadora-9", "carga-42")
    args_iniciar = cliente.iniciar_viagem.call_args.args
    assert args_iniciar[0] == "transportadora-9"
    assert args_iniciar[2] == "carga-42"
