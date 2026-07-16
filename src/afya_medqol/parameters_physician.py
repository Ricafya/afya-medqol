"""Psychometric parameters for the 2024_2 calibration, frozen in source code.

Source: Gobbo Jr M et al., BMJ Open 2025;15:e102783 (2024_2 calibration, n=2005).
Extracted from ``Tabela_Parametros_AfyaMedQoL_2024_2.xlsx``. Changing the
calibration in the future means editing the values below, not swapping an
external file.
"""

from __future__ import annotations

from typing import Any, NamedTuple

import numpy as np

from .constants_physician import ITENS_TODOS, N_CATEGORIES


class _ItemParams(NamedTuple):
    item: str
    factor: str
    a: float
    b: tuple[float, float, float, float]


# item, factor, discrimination (a), thresholds (b1..b4)
_ITEM_PARAMS: tuple[_ItemParams, ...] = (
    _ItemParams("F1_1_enjoymentoflife", "F1", 2.25907121489438,
                (-2.27022061237598, -0.638638147989716, 0.737967867913462, 2.387662462197)),
    _ItemParams("F1_2_financialsufficiency", "F1", 1.43988656804336,
                (-2.88038772129706, -1.55144738619884, 0.370167224112102, 1.66953061443787)),
    _ItemParams("F1_3_accesstoinformation", "F1", 1.28517933612724,
                (-4.9203033999288, -2.87087290365195, -0.899592341977996, 1.33015941289966)),
    _ItemParams("F1_4_leisureopportunities", "F1", 2.83155139639134,
                (-2.12786846120779, -0.532472285599668, 0.660486991465796, 1.9367909238368)),
    _ItemParams("F1_5_mobilitypast2weeks", "F1", 1.11754238612949,
                (-4.73905600129992, -3.38948129597766, -1.98142794363967, -0.0887479065707152)),
    _ItemParams("F1_6_accesstohealthservices", "F1", 1.1327871651721,
                (-3.41730782382212, -1.83460779259542, -0.714888966003369, 1.41467272927244)),
    _ItemParams("F2_1_technicaltraining", "F2", 1.81350717883516,
                (-0.713055200732724, -0.136651950577718, 0.250200016868484, 1.3323609703848)),
    _ItemParams("F2_2_mentalhealthsupport", "F2", 2.3940524041242,
                (0.0483251423465849, 0.469839203582854, 1.0193844967889, 1.70219075356324)),
    _ItemParams("F2_3_coworkersupportnetwork", "F2", 1.97250252841685,
                (-0.855213512788996, -0.199010428068228, 0.366349461968555, 1.56498904613744)),
    _ItemParams("F2_4_educationalhandlingoferrors", "F2", 2.31427873406568,
                (-0.73519953639222, -0.198751964266666, 0.636231791454835, 1.51654705896202)),
    _ItemParams("F3_1_stresshurtsperformance", "F3", 2.82679109871707,
                (-1.37691846703211, -0.663976699419235, -0.285706187843931, 0.789980214380672)),
    _ItemParams("F3_2_stressledtoerrors", "F3", 1.50927971357202,
                (-0.719197859705559, 0.0600525662835842, 0.649884192197721, 2.00042396166554)),
    _ItemParams("F3_3_stresshurtsrelationships", "F3", 2.5121096734455,
                (-1.52520413707683, -0.982164523763152, -0.6498451775552, 0.448475958974047)),
)

# Independent domains by construction (simple structure: 1 item -> 1 factor).
_SIGMA = np.array([
    [1.0, 0.0, 0.0],
    [0.0, 1.0, 0.0],
    [0.0, 0.0, 1.0],
])

# Global score weights: Σ|a| of the factor / total Σ|a|.
_PESOS = np.array([0.3961667339121522, 0.3343104738296151, 0.2695227922582326])

# F3 (Stress) is reversed only in the global score composite, per the article.
_F3_REVERSE_GLOBAL = True

_FACTOR_COL = {"F1": 0, "F2": 1, "F3": 2}


def load_parameters_physician() -> dict[str, Any]:
    """Build the 2024_2 calibration parameters dict (fixed, no I/O)."""
    A = np.zeros((len(_ITEM_PARAMS), 3))
    B = np.zeros((len(_ITEM_PARAMS), N_CATEGORIES - 1))
    for i, p in enumerate(_ITEM_PARAMS):
        A[i, _FACTOR_COL[p.factor]] = p.a
        B[i] = p.b

    return {
        "A": A, "B": B, "SIGMA": _SIGMA, "WEIGHTS": _PESOS,
        "F3_REVERSE_GLOBAL": _F3_REVERSE_GLOBAL,
        "ITEMS": ITENS_TODOS,
    }
