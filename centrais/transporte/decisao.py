from __future__ import annotations

from dataclasses import dataclass

MULTIPLICADORES_POR_MODO = {
    "economico": {"energia": 0.85, "degradacao": 2.5},
    "normal":    {"energia": 1.00, "degradacao": 1.0},
    "rapido":    {"energia": 1.05, "degradacao": 0.5},
}

PRECO_POR_MINERAL = {
    "hematita": 5.0,
    "silica_de_alta_pureza": 20.0,
    "jarosita": 35.0,
    "gelo_de_agua": 40.0,
    "cristal_marciano_raro": 200.0,
}
PRECO_PADRAO = 5.0


def obter_valor_por_kg(mineral: str) -> float:
    return PRECO_POR_MINERAL.get(mineral, PRECO_PADRAO)


@dataclass
class Candidata:
    rota: dict
    modo: str
    pontuacao: float


def escolher_rota_e_modo(carga: dict, rotas_livres: list[dict], valor_por_kg: float) -> Candidata:
    melhor: Candidata | None = None
    for rota in rotas_livres:
        for modo, multiplicador in MULTIPLICADORES_POR_MODO.items():
            degradacao_estimada = rota["multiplicador_degradacao"] * multiplicador["degradacao"]
            valor_preservado = carga["quantidade"] * valor_por_kg * (1 - min(degradacao_estimada, 1.0) * 0.1)
            custo_energia = rota["custo_energia_base"] * multiplicador["energia"]
            pontuacao = valor_preservado - custo_energia

            candidata = Candidata(rota=rota, modo=modo, pontuacao=pontuacao)
            if melhor is None or candidata.pontuacao > melhor.pontuacao:
                melhor = candidata

    if melhor is None:
        raise ValueError("Não foi encontrada rota adequada para a carga.")
    return melhor
