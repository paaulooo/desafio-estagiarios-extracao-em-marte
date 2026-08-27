from __future__ import annotations

from fastapi import FastAPI, Request

from centrais.transporte.decisao import obter_valor_por_kg
from centrais.transporte.orquestrador import despachar_carga
from centrais.transporte.transporte_client import ClienteDeMissao, ClienteDeTransporte

app = FastAPI(title="Central de Transporte")

_cliente = ClienteDeTransporte()
_missao = ClienteDeMissao()


def _unidade_disponivel() -> dict | None:
    for transportadora in _cliente.consultar_transportadores():
        if transportadora["estado"] == "disponivel":
            return transportadora
    return None


def _tentar_despachar(identificador_da_carga: str) -> None:
    cargas = _cliente.consultar_cargas_disponiveis()
    carga = next((c for c in cargas if c["identificador"] == identificador_da_carga), None)
    if carga is None:
        return

    unidade = _unidade_disponivel()
    if unidade is None:
        return

    valor_por_kg = obter_valor_por_kg(carga["mineral"])
    try:
        despachar_carga(_cliente, _missao, carga, unidade["identificador"], valor_por_kg)
    except Exception:
        # Evento fire-and-forget: uma falha de despacho (rota indisponível,
        # precondição violada no motor) não pode derrubar o webhook.
        pass


def tratar_carga_nova(identificador_da_carga: str) -> None:
    _tentar_despachar(identificador_da_carga)


def liberar_unidade(identificador_da_unidade: str, identificador_da_carga: str) -> None:
    try:
        _cliente.descarregar(identificador_da_unidade, identificador_da_carga)
        _cliente.retornar_unidade(identificador_da_unidade)
    except Exception:
        pass


def reavaliar_carga(identificador_da_carga: str, identificador_da_unidade: str) -> None:
    try:
        _cliente.retornar_unidade(identificador_da_unidade)
    except Exception:
        pass
    _tentar_despachar(identificador_da_carga)


@app.post("/webhooks/transporte")
async def receber_evento(requisicao: Request) -> dict:
    evento = await requisicao.json()
    tipo = evento.get("tipo")
    dados = evento.get("dados", {})

    if tipo in ("extracao_concluida", "carga_disponivel"):
        tratar_carga_nova(dados["carga"])
    elif tipo == "transporte_concluido":
        liberar_unidade(dados["unidade"], dados["carga"])
    elif tipo == "viagem_abortada":
        reavaliar_carga(dados["carga"], dados["unidade"])

    return {"ok": True}
