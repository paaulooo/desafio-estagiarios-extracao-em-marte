from __future__ import annotations

from centrais.missao.orquestrador import executar_ciclo_de_gestao


class _ClienteFake:
    def __init__(self, estado: dict):
        self._estado = estado
        self.chamadas = []

    def chamar(self, metodo, rota, json=None):
        self.chamadas.append((metodo, rota, json))
        if rota == "/missao/estado":
            return self._estado
        return {"aceito": True}


def test_nao_aloca_energia_quando_todas_as_centrais_estao_saudaveis():
    cliente = _ClienteFake({"energia": {
        "extracao": 10.0, "armazenagem": 10.0, "transporte": 10.0, "pesquisa": 10.0, "missao": 10.0,
    }})

    resultados = executar_ciclo_de_gestao(cliente)

    assert resultados == []
    assert cliente.chamadas == [("GET", "/missao/estado", None)]


def test_aloca_energia_para_central_com_pouca_energia():
    cliente = _ClienteFake({"energia": {
        "extracao": 1.0, "armazenagem": 10.0, "transporte": 10.0, "pesquisa": 10.0, "missao": 10.0,
    }})

    resultados = executar_ciclo_de_gestao(cliente)

    assert resultados == [{"aceito": True}]
    assert cliente.chamadas == [
        ("GET", "/missao/estado", None),
        ("POST", "/missao/alocar-energia", {"destino": "extracao", "quantidade": 20, "politica": "contingencia"}),
    ]


def test_aloca_energia_para_varias_centrais_em_um_unico_ciclo():
    cliente = _ClienteFake({"energia": {
        "extracao": 1.0, "armazenagem": 1.0, "transporte": 10.0, "pesquisa": 10.0, "missao": 10.0,
    }})

    resultados = executar_ciclo_de_gestao(cliente)

    assert len(resultados) == 2
    rotas_chamadas = [chamada[1] for chamada in cliente.chamadas]
    assert rotas_chamadas.count("/missao/alocar-energia") == 2
