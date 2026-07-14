"""Constantes do modelo Afya MedQoL (calibração 2024_2)."""

from __future__ import annotations

ITENS_F1 = [
    "F1_1_enjoymentoflife", "F1_2_financialsufficiency", "F1_3_accesstoinformation",
    "F1_4_leisureopportunities", "F1_5_mobilitypast2weeks", "F1_6_accesstohealthservices",
]
ITENS_F2 = [
    "F2_1_technicaltraining", "F2_2_mentalhealthsupport",
    "F2_3_coworkersupportnetwork", "F2_4_educationalhandlingoferrors",
]
ITENS_F3 = [
    "F3_1_stresshurtsperformance", "F3_2_stressledtoerrors", "F3_3_stresshurtsrelationships",
]
ITENS_TODOS = ITENS_F1 + ITENS_F2 + ITENS_F3

N_CATEGORIAS = 5
N_GRID = 25
