from __future__ import annotations

from centrais.missao.cliente_de_missao import alocar_energia, consultar_estado
from centrais.missao.decisao import decidir_alocacoes


def executar_ciclo_de_gestao(cliente) -> list[dict]:
    estado = consultar_estado(cliente)
    decisoes = decidir_alocacoes(estado)
    return [
        alocar_energia(cliente, destino=decisao.destino, quantidade=decisao.quantidade, politica=decisao.politica)
        for decisao in decisoes
    ]
