from __future__ import annotations

import requests


class ClienteDeTransporte:
    def __init__(self, base_url: str = "http://localhost:8000", sessao: requests.Session | None = None):
        self._base_url = base_url
        self._sessao = sessao or requests.Session()

    def consultar_rotas(self) -> list[dict]:
        resposta = self._sessao.get(f"{self._base_url}/transporte/rotas")
        resposta.raise_for_status()
        return resposta.json()

    def consultar_transportadores(self) -> list[dict]:
        resposta = self._sessao.get(f"{self._base_url}/transporte/transportadores")
        resposta.raise_for_status()
        return resposta.json()

    def consultar_cargas_disponiveis(self) -> list[dict]:
        resposta = self._sessao.get(f"{self._base_url}/transporte/cargas-disponiveis")
        resposta.raise_for_status()
        return resposta.json()

    def planejar_transporte(self, identificador_da_carga: str) -> dict:
        resposta = self._sessao.get(
            f"{self._base_url}/transporte/planejar-transporte",
            params={"identificador_da_carga": identificador_da_carga},
        )
        resposta.raise_for_status()
        return resposta.json()

    def carregar(self, identificador_da_unidade: str, identificador_da_carga: str) -> dict:
        resposta = self._sessao.post(f"{self._base_url}/transporte/carregar", json={
            "identificador_da_unidade": identificador_da_unidade,
            "identificador_da_carga": identificador_da_carga,
        })
        resposta.raise_for_status()
        return resposta.json()

    def iniciar_viagem(
        self, identificador_da_unidade: str, identificador_da_rota: str,
        identificador_da_carga: str, id_autorizacao: str, modo: str = "normal",
    ) -> dict:
        resposta = self._sessao.post(f"{self._base_url}/transporte/iniciar-viagem", json={
            "identificador_da_unidade": identificador_da_unidade,
            "identificador_da_rota": identificador_da_rota,
            "identificador_da_carga": identificador_da_carga,
            "id_autorizacao": id_autorizacao,
            "modo": modo,
        })
        resposta.raise_for_status()
        return resposta.json()

    def descarregar(self, identificador_da_unidade: str, identificador_da_carga: str) -> dict:
        resposta = self._sessao.post(f"{self._base_url}/transporte/descarregar", json={
            "identificador_da_unidade": identificador_da_unidade,
            "identificador_da_carga": identificador_da_carga,
        })
        resposta.raise_for_status()
        return resposta.json()

    def retornar_unidade(self, identificador_da_unidade: str) -> dict:
        resposta = self._sessao.post(f"{self._base_url}/transporte/retornar-unidade", json={
            "identificador_da_unidade": identificador_da_unidade,
        })
        resposta.raise_for_status()
        return resposta.json()


class ClienteDeMissao:
    def __init__(self, base_url: str = "http://localhost:8000", sessao: requests.Session | None = None):
        self._base_url = base_url
        self._sessao = sessao or requests.Session()

    def autorizar_missao(self, operacao: str, central_solicitante: str, classe: str = "rapida") -> dict:
        resposta = self._sessao.post(f"{self._base_url}/missao/autorizar-missao", json={
            "operacao": operacao,
            "central_solicitante": central_solicitante,
            "classe": classe,
        })
        resposta.raise_for_status()
        return resposta.json()

    def registrar_webhook(self, url: str) -> dict:
        resposta = self._sessao.post(f"{self._base_url}/missao/registrar-webhook", json={"url": url})
        resposta.raise_for_status()
        return resposta.json()
