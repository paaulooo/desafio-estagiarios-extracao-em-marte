from __future__ import annotations

from typing import Any, Protocol


class ClienteComChamar(Protocol):
    def chamar(self, metodo: str, rota: str, json: dict | None = None) -> Any: ...


def resetar_mundo(cliente: ClienteComChamar, semente: int, duracao_maxima: int | None = None) -> dict:
    return cliente.chamar("POST", "/missao/resetar-mundo", json={
        "semente": semente,
        "duracao_maxima": duracao_maxima,
    })


def consultar_estado(cliente: ClienteComChamar) -> dict:
    return cliente.chamar("GET", "/missao/estado")


def consultar_eventos(cliente: ClienteComChamar, desde_ciclo: int = 0) -> list[dict]:
    return cliente.chamar("GET", f"/missao/eventos?desde_ciclo={desde_ciclo}")


def alocar_energia(
    cliente: ClienteComChamar, destino: str, quantidade: int, politica: str = "pulso",
) -> dict:
    return cliente.chamar("POST", "/missao/alocar-energia", json={
        "destino": destino,
        "quantidade": quantidade,
        "politica": politica,
    })


def autorizar(
    cliente: ClienteComChamar, operacao: str, central_solicitante: str, classe: str = "rapida",
) -> str:
    resposta = cliente.chamar("POST", "/missao/autorizar-missao", json={
        "operacao": operacao,
        "central_solicitante": central_solicitante,
        "classe": classe,
    })
    return resposta["id_autorizacao"]


def registrar_webhook(cliente: ClienteComChamar, url: str) -> dict:
    return cliente.chamar("POST", "/missao/registrar-webhook", json={"url": url})
