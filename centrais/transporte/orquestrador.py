from __future__ import annotations

from .transporte_client import ClienteDeMissao, ClienteDeTransporte
from .decisao import escolher_rota_e_modo


def despachar_carga(
    cliente: ClienteDeTransporte,
    missao: ClienteDeMissao,
    carga: dict,
    identificador_da_unidade: str,
    valor_por_kg: float,
) -> dict:
    plano = cliente.planejar_transporte(carga["identificador"])
    todas_as_rotas = cliente.consultar_rotas()
    rotas_livres = [r for r in todas_as_rotas if r["identificador"] in plano["rotas_disponiveis"]]

    candidata = escolher_rota_e_modo(carga, rotas_livres, valor_por_kg)

    autorizacao = missao.autorizar_missao(
        operacao="iniciar_viagem", central_solicitante="transporte",
    )["id_autorizacao"]

    cliente.carregar(identificador_da_unidade, carga["identificador"])
    return cliente.iniciar_viagem(
        identificador_da_unidade,
        candidata.rota["identificador"],
        carga["identificador"],
        autorizacao,
        candidata.modo,
    )