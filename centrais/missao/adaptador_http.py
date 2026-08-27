from __future__ import annotations

import requests


class ClienteHttp:
    def __init__(self, base_url: str = "http://localhost:8000", sessao: requests.Session | None = None):
        self._base_url = base_url
        self._sessao = sessao or requests.Session()

    def chamar(self, metodo: str, rota: str, json: dict | None = None) -> dict:
        resposta = self._sessao.request(metodo, f"{self._base_url}{rota}", json=json)
        resposta.raise_for_status()
        return resposta.json()
