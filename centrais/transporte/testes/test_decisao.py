from __future__ import annotations

import pytest

from centrais.transporte.decisao import escolher_rota_e_modo, obter_valor_por_kg


def test_prefere_rota_mais_barata_quando_degradacao_e_igual():
    carga = {"quantidade": 10.0}
    rotas = [
        {"identificador": "rota-1", "custo_energia_base": 3.0, "multiplicador_degradacao": 1.0},
        {"identificador": "rota-2", "custo_energia_base": 5.0, "multiplicador_degradacao": 1.0},
    ]

    candidata = escolher_rota_e_modo(carga, rotas, valor_por_kg=10.0)

    assert candidata.rota["identificador"] == "rota-1"


def test_avalia_todas_as_rotas_nao_so_a_primeira():
    carga = {"quantidade": 10.0}
    rotas = [
        {"identificador": "rota-cara", "custo_energia_base": 50.0, "multiplicador_degradacao": 1.0},
        {"identificador": "rota-barata", "custo_energia_base": 1.0, "multiplicador_degradacao": 1.0},
    ]

    candidata = escolher_rota_e_modo(carga, rotas, valor_por_kg=10.0)

    assert candidata.rota["identificador"] == "rota-barata"


def test_funciona_com_uma_unica_rota_livre():
    carga = {"quantidade": 5.0}
    rotas = [{"identificador": "rota-1", "custo_energia_base": 3.0, "multiplicador_degradacao": 1.0}]

    candidata = escolher_rota_e_modo(carga, rotas, valor_por_kg=20.0)

    assert candidata.rota["identificador"] == "rota-1"
    assert candidata.modo in ("economico", "normal", "rapido")


def test_sem_rotas_livres_levanta_erro():
    with pytest.raises(ValueError):
        escolher_rota_e_modo({"quantidade": 10.0}, [], valor_por_kg=10.0)


def test_carga_valiosa_favorece_modo_rapido_sobre_economico():
    # Com valor_por_kg alto, preservar qualidade pesa muito mais que a
    # pequena diferença de custo energético entre os modos.
    carga = {"quantidade": 10.0}
    rota_unica = {"identificador": "rota-1", "custo_energia_base": 3.0, "multiplicador_degradacao": 0.3}

    candidata = escolher_rota_e_modo(carga, [rota_unica], valor_por_kg=1000.0)

    assert candidata.modo == "rapido"


def test_obter_valor_por_kg_usa_tabela_de_precos_conhecida():
    assert obter_valor_por_kg("cristal_marciano_raro") == 200.0
    assert obter_valor_por_kg("hematita") == 5.0


def test_obter_valor_por_kg_usa_preco_padrao_para_mineral_desconhecido():
    assert obter_valor_por_kg("mineral_nunca_visto") == 5.0
