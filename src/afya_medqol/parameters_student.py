"""Psychometric parameters for the IQoL (medical students), frozen in source code.

Source: Gobbo M Jr et al., "Development and psychometric validation of the
8-item Student Quality of Life Index (IQoL) using item response theory
(IRT)", BMJ Open 2026;16:e106371 (N=10844). Extracted from
``Tabela_Parametros_IQoL.csv`` and ``Constantes_Calibracao_IQoL.csv``. Changing
the calibration in the future means editing the values below, not swapping
an external file.
"""

from __future__ import annotations

from typing import Any, NamedTuple


class _StudentItemParams(NamedTuple):
    item: str
    factor: int
    domain: str
    aG: float
    aS: float
    d: tuple[float, float, float, float]


# item, factor (1=psychological well-being, 2=vitality, 3=perceived functional
# capacity), domain name, general discrimination (aG), specific discrimination
# (aS), thresholds (d1..d4)
_STUDENT_ITEM_PARAMS: tuple[_StudentItemParams, ...] = (
    _StudentItemParams("F1_1_overallqol", 1, "psychological_well_being", 2.00, 1.77,
                         (6.45, 4.44, 1.58, -2.41)),
    _StudentItemParams("F1_2_satisfactionwithhealth", 1, "psychological_well_being", 1.65, 0.91,
                         (4.41, 1.99, 0.13, -2.98)),
    _StudentItemParams("F1_3_enjoymentoflife", 1, "psychological_well_being", 1.57, 0.76,
                         (4.90, 2.31, -0.17, -3.15)),
    _StudentItemParams("F1_4_perceivedmeaninginlife", 1, "psychological_well_being", 1.37, 0.51,
                         (4.59, 2.96, 1.09, -1.03)),
    _StudentItemParams("F2_1_energyfordailyactivities", 2, "vitality", 2.50, -0.74,
                         (5.88, 2.60, -1.42, -4.12)),
    _StudentItemParams("F2_2_satisfactionwithsleep", 2, "vitality", 2.25, 0.85,
                         (4.19, 1.67, -0.45, -3.76)),
    _StudentItemParams("F3_1_performdailyactivities", 3, "perceived_functional_capacity", 3.48, 1.61,
                         (6.96, 3.45, -0.11, -5.49)),
    _StudentItemParams("F3_2_capacityforwork", 3, "perceived_functional_capacity", 2.33, 1.22,
                         (5.14, 2.76, 0.07, -3.90)),
)

# Domain weight in the global score (relative Σ|a|, frozen from the calibration).
_PESOS_ESTUDANTE = {1: 0.494, 2: 0.172, 3: 0.335}

# Mean/SD of theta_global in the reference sample (for T-score).
_MU_G = -0.0007975659350793075
_SIGMA_G = 0.33762207315881504

_DOMAIN_NAME = {1: "psychological_well_being", 2: "vitality", 3: "perceived_functional_capacity"}


def load_parameters_student() -> dict[str, Any]:
    """Build the IQoL parameters dict (fixed, no I/O)."""
    items: dict[str, dict[str, Any]] = {}
    domains: dict[int, list[str]] = {}
    for p in _STUDENT_ITEM_PARAMS:
        items[p.item] = {"aG": p.aG, "aS": p.aS, "d": p.d, "factor": p.factor}
        domains.setdefault(p.factor, []).append(p.item)

    return {
        "ITEMS": items,
        "DOMAINS": domains,
        "WEIGHTS": _PESOS_ESTUDANTE,
        "MU_G": _MU_G,
        "SIGMA_G": _SIGMA_G,
        "DOMAIN_NAME": _DOMAIN_NAME,
    }
