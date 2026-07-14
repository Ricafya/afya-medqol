"""Parâmetros psicométricos do IQoL (estudantes de medicina), fixados no código-fonte.

Fonte: Gobbo M Jr et al., "Development and psychometric validation of the
8-item Student Quality of Life Index (IQoL) using item response theory
(IRT)", BMJ Open 2026;16:e106371 (N=10844). Extraídos de
``Tabela_Parametros_IQoL.csv`` e ``Constantes_Calibracao_IQoL.csv``. Trocar
de calibração no futuro significa editar os valores abaixo, não trocar um
arquivo externo.
"""

from __future__ import annotations

from typing import Any, NamedTuple


class _ItemParamsEstudante(NamedTuple):
    item: str
    fator: int
    dominio: str
    aG: float
    aS: float
    d: tuple[float, float, float, float]


# item, fator (1=bem-estar psicológico, 2=vitalidade, 3=capacidade funcional),
# nome do domínio, discriminação geral (aG), discriminação específica (aS),
# thresholds (d1..d4)
_ITENS_PARAMS_ESTUDANTE: tuple[_ItemParamsEstudante, ...] = (
    _ItemParamsEstudante("F1_1_overallqol", 1, "bem_estar_psicologico", 2.00, 1.77,
                         (6.45, 4.44, 1.58, -2.41)),
    _ItemParamsEstudante("F1_2_satisfactionwithhealth", 1, "bem_estar_psicologico", 1.65, 0.91,
                         (4.41, 1.99, 0.13, -2.98)),
    _ItemParamsEstudante("F1_3_enjoymentoflife", 1, "bem_estar_psicologico", 1.57, 0.76,
                         (4.90, 2.31, -0.17, -3.15)),
    _ItemParamsEstudante("F1_4_perceivedmeaninginlife", 1, "bem_estar_psicologico", 1.37, 0.51,
                         (4.59, 2.96, 1.09, -1.03)),
    _ItemParamsEstudante("F2_1_energyfordailyactivities", 2, "vitalidade", 2.50, -0.74,
                         (5.88, 2.60, -1.42, -4.12)),
    _ItemParamsEstudante("F2_2_satisfactionwithsleep", 2, "vitalidade", 2.25, 0.85,
                         (4.19, 1.67, -0.45, -3.76)),
    _ItemParamsEstudante("F3_1_performdailyactivities", 3, "capacidade_funcional", 3.48, 1.61,
                         (6.96, 3.45, -0.11, -5.49)),
    _ItemParamsEstudante("F3_2_capacityforwork", 3, "capacidade_funcional", 2.33, 1.22,
                         (5.14, 2.76, 0.07, -3.90)),
)

# Peso do domínio no escore global (Σ|a| relativo, congelado da calibração).
_PESOS_ESTUDANTE = {1: 0.494, 2: 0.172, 3: 0.335}

# Média/DP do theta_global na amostra de referência (para T-score).
_MU_G = -0.0007975659350793075
_SIGMA_G = 0.33762207315881504

_NOME_DOMINIO = {1: "bem_estar_psicologico", 2: "vitalidade", 3: "capacidade_funcional"}


def carregar_parametros_estudante() -> dict[str, Any]:
    """Monta o dicionário de parâmetros do IQoL (fixo, sem I/O)."""
    itens: dict[str, dict[str, Any]] = {}
    dominios: dict[int, list[str]] = {}
    for p in _ITENS_PARAMS_ESTUDANTE:
        itens[p.item] = {"aG": p.aG, "aS": p.aS, "d": p.d, "fator": p.fator}
        dominios.setdefault(p.fator, []).append(p.item)

    return {
        "ITENS": itens,
        "DOMINIOS": dominios,
        "PESOS": _PESOS_ESTUDANTE,
        "MU_G": _MU_G,
        "SIGMA_G": _SIGMA_G,
        "NOME_DOMINIO": _NOME_DOMINIO,
    }
