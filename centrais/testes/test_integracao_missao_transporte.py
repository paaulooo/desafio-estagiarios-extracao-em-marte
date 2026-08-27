from __future__ import annotations

from fastapi.testclient import TestClient

from centrais.missao.orquestrador import executar_ciclo_de_gestao
from centrais.transporte.decisao import obter_valor_por_kg
from centrais.transporte.orquestrador import despachar_carga
from centrais.transporte.transporte_client import ClienteDeMissao, ClienteDeTransporte
from mundo.api.app import criar_app
from mundo.api.dependencias import obter_motor


class _ClienteDeMissaoGenerico:
    """Adapta o TestClient para a interface .chamar(...) usada por centrais/missao,
    a mesma que o ClienteDeAvaliacao expõe no avaliador real."""

    def __init__(self, cliente_http):
        self._cliente_http = cliente_http

    def chamar(self, metodo: str, rota: str, json: dict | None = None):
        resposta = self._cliente_http.request(metodo, rota, json=json)
        resposta.raise_for_status()
        return resposta.json()


def _avancar_ate_haver_carga(cliente_http, maximo_de_ciclos: int = 20) -> dict:
    motor = obter_motor()
    for _ in range(maximo_de_ciclos):
        motor.avancar_ciclo()
        cargas = cliente_http.get("/transporte/cargas-disponiveis").json()
        if cargas:
            return cargas[0]
    raise AssertionError("Nenhuma carga ficou disponível a tempo")


def test_missao_e_transporte_cooperam_no_despacho_de_uma_carga_real():
    with TestClient(criar_app(com_loop_real_time=False)) as cliente_http:
        cliente_http.post("/missao/resetar-mundo", json={"semente": 0}).raise_for_status()

        cliente_transporte = ClienteDeTransporte(base_url="", sessao=cliente_http)
        cliente_missao_do_transporte = ClienteDeMissao(base_url="", sessao=cliente_http)
        cliente_missao_generico = _ClienteDeMissaoGenerico(cliente_http)

        # a Central de Missão garante energia suficiente antes de qualquer operação
        assert executar_ciclo_de_gestao(cliente_missao_generico) == []

        mineradora = next(m for m in cliente_http.get("/extracao/mineradoras").json() if m["estado"] == "disponivel")
        jazida = next(j for j in cliente_http.get("/extracao/jazidas").json() if j["estado"] == "disponivel")
        resposta = cliente_http.post("/extracao/iniciar-extracao", json={
            "identificador_da_unidade": mineradora["identificador"],
            "identificador_da_jazida": jazida["identificador"],
            "quantidade": 10.0,
        })
        resposta.raise_for_status()

        carga = _avancar_ate_haver_carga(cliente_http)
        assert carga["mineral"] == jazida["mineral"]

        transportadora = next(
            t for t in cliente_transporte.consultar_transportadores() if t["estado"] == "disponivel"
        )

        resultado = despachar_carga(
            cliente_transporte, cliente_missao_do_transporte, carga,
            transportadora["identificador"], obter_valor_por_kg(carga["mineral"]),
        )
        assert resultado == {"aceito": True}

        obter_motor().avancar_ciclo()  # aplica carregar + iniciar-viagem, ambos enfileirados

        transportadora_apos = next(
            t for t in cliente_transporte.consultar_transportadores()
            if t["identificador"] == transportadora["identificador"]
        )
        assert transportadora_apos["estado"] == "executando"

        estado_da_missao = cliente_missao_generico.chamar("GET", "/missao/estado")
        assert estado_da_missao["energia"]["missao"] < 10.0  # custo da autorização + consumo passivo
