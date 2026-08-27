from __future__ import annotations

from centrais.missao.decisao import decidir_alocacoes


def _estado_com_energia(**energia) -> dict:
    return {"ciclo_atual": 10, "energia": energia, "faturamento_total": 0.0}


def test_nenhuma_alocacao_quando_todas_as_centrais_estao_saudaveis():
    estado = _estado_com_energia(
        extracao=10.0, armazenagem=10.0, transporte=10.0, pesquisa=10.0, missao=10.0, reserva_estrategica=950.0,
    )

    assert decidir_alocacoes(estado) == []


def test_propoe_reposicao_para_central_abaixo_do_limiar():
    estado = _estado_com_energia(
        extracao=1.5, armazenagem=10.0, transporte=10.0, pesquisa=10.0, missao=10.0, reserva_estrategica=950.0,
    )

    decisoes = decidir_alocacoes(estado)

    assert len(decisoes) == 1
    assert decisoes[0].destino == "extracao"
    assert decisoes[0].politica == "contingencia"


def test_usa_politica_pulso_quando_o_destino_e_a_propria_missao():
    estado = _estado_com_energia(
        extracao=10.0, armazenagem=10.0, transporte=10.0, pesquisa=10.0, missao=2.0, reserva_estrategica=950.0,
    )

    decisoes = decidir_alocacoes(estado)

    assert decisoes == [("missao", 20, "pulso")]


def test_propoe_reposicao_para_multiplas_centrais_simultaneamente():
    estado = _estado_com_energia(
        extracao=1.0, armazenagem=1.0, transporte=10.0, pesquisa=10.0, missao=10.0, reserva_estrategica=950.0,
    )

    decisoes = decidir_alocacoes(estado)

    destinos = {decisao.destino for decisao in decisoes}
    assert destinos == {"extracao", "armazenagem"}


def test_central_ausente_do_estado_e_tratada_como_sem_energia():
    estado = _estado_com_energia(extracao=10.0, armazenagem=10.0, transporte=10.0, pesquisa=10.0)

    decisoes = decidir_alocacoes(estado)

    assert decisoes == [("missao", 20, "pulso")]
