from __future__ import annotations

from typing import NamedTuple

CENTRAIS_OPERANTES = ("extracao", "armazenagem", "transporte", "pesquisa", "missao")
LIMIAR_DE_ENERGIA_BAIXA = 3.0
QUANTIDADE_DE_REPOSICAO = 20


class DecisaoDeAlocacao(NamedTuple):
    destino: str
    quantidade: int
    politica: str


def decidir_alocacoes(estado: dict) -> list[DecisaoDeAlocacao]:
    energia = estado.get("energia", {})
    decisoes = []
    for central in CENTRAIS_OPERANTES:
        saldo = energia.get(central, 0.0)
        if saldo < LIMIAR_DE_ENERGIA_BAIXA:
            politica = "pulso" if central == "missao" else "contingencia"
            decisoes.append(DecisaoDeAlocacao(central, QUANTIDADE_DE_REPOSICAO, politica))
    return decisoes
