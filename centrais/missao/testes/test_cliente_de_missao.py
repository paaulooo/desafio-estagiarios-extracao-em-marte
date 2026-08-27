from __future__ import annotations

from centrais.missao import cliente_de_missao


class _ClienteFake:
    def __init__(self, retorno=None):
        self.chamadas = []
        self._retorno = retorno

    def chamar(self, metodo, rota, json=None):
        self.chamadas.append((metodo, rota, json))
        return self._retorno


def test_resetar_mundo_envia_semente_e_duracao_maxima():
    cliente = _ClienteFake(retorno={"ciclo_atual": 0})

    resultado = cliente_de_missao.resetar_mundo(cliente, semente=7, duracao_maxima=100)

    assert cliente.chamadas == [
        ("POST", "/missao/resetar-mundo", {"semente": 7, "duracao_maxima": 100}),
    ]
    assert resultado == {"ciclo_atual": 0}


def test_consultar_estado_chama_rota_correta():
    cliente = _ClienteFake(retorno={"ciclo_atual": 5, "energia": {}, "faturamento_total": 0.0})

    resultado = cliente_de_missao.consultar_estado(cliente)

    assert cliente.chamadas == [("GET", "/missao/estado", None)]
    assert resultado["ciclo_atual"] == 5


def test_consultar_eventos_usa_desde_ciclo_na_query_string():
    cliente = _ClienteFake(retorno=[])

    cliente_de_missao.consultar_eventos(cliente, desde_ciclo=42)

    assert cliente.chamadas == [("GET", "/missao/eventos?desde_ciclo=42", None)]


def test_consultar_eventos_usa_zero_por_padrao():
    cliente = _ClienteFake(retorno=[])

    cliente_de_missao.consultar_eventos(cliente)

    assert cliente.chamadas == [("GET", "/missao/eventos?desde_ciclo=0", None)]


def test_alocar_energia_envia_destino_quantidade_e_politica():
    cliente = _ClienteFake(retorno={"aceito": True})

    resultado = cliente_de_missao.alocar_energia(cliente, destino="transporte", quantidade=3, politica="contingencia")

    assert cliente.chamadas == [
        ("POST", "/missao/alocar-energia", {"destino": "transporte", "quantidade": 3, "politica": "contingencia"}),
    ]
    assert resultado == {"aceito": True}


def test_alocar_energia_usa_politica_pulso_por_padrao():
    cliente = _ClienteFake(retorno={"aceito": True})

    cliente_de_missao.alocar_energia(cliente, destino="extracao", quantidade=1)

    assert cliente.chamadas == [
        ("POST", "/missao/alocar-energia", {"destino": "extracao", "quantidade": 1, "politica": "pulso"}),
    ]


def test_autorizar_retorna_apenas_o_identificador():
    cliente = _ClienteFake(retorno={"id_autorizacao": "auth-123"})

    identificador = cliente_de_missao.autorizar(cliente, operacao="iniciar-viagem", central_solicitante="transporte")

    assert identificador == "auth-123"
    assert cliente.chamadas == [
        ("POST", "/missao/autorizar-missao", {
            "operacao": "iniciar-viagem", "central_solicitante": "transporte", "classe": "rapida",
        }),
    ]


def test_autorizar_repassa_classe_explicita():
    cliente = _ClienteFake(retorno={"id_autorizacao": "auth-456"})

    cliente_de_missao.autorizar(cliente, operacao="lote-x", central_solicitante="armazenagem", classe="lote")

    assert cliente.chamadas == [
        ("POST", "/missao/autorizar-missao", {
            "operacao": "lote-x", "central_solicitante": "armazenagem", "classe": "lote",
        }),
    ]


def test_registrar_webhook_envia_url():
    cliente = _ClienteFake(retorno={"registrado": True})

    resultado = cliente_de_missao.registrar_webhook(cliente, url="http://localhost:9000/webhooks/missao")

    assert cliente.chamadas == [
        ("POST", "/missao/registrar-webhook", {"url": "http://localhost:9000/webhooks/missao"}),
    ]
    assert resultado == {"registrado": True}
