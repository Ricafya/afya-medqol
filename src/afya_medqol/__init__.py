"""Afya MedQoL — cálculo do índice de qualidade de vida para médicos.

Samejima GRM 3D com domínios independentes, escoragem EAP, calibração
2024_2 (Gobbo Jr M et al., BMJ Open 2025;15:e102783), escoragem 100%
determinística (quadratura fixa, sem semente)::

    from afya_medqol import MedQoLPhysicianCalculator

    calc = MedQoLPhysicianCalculator()
    resultado = calc.score_batch(df_respostas)
    resultado_unico = calc.score_physician({"F1_1_enjoymentoflife": 4, ...})
    calc.item_questions()["F1_1_enjoymentoflife"]  # -> texto original (inglês)
    calc.item_questions(lang="pt")["F1_1_enjoymentoflife"]  # -> texto original (português)
    calc.item_options(lang="pt")["F1_1_enjoymentoflife"]  # -> ["Nada (1)", ..., "Extremamente (5)"]
    calc.factor_items  # -> {"Factor1": [...6 itens...], "Factor2": [...4 itens...], "Factor3": [...3 itens...]}
"""

from importlib.metadata import PackageNotFoundError, version

from .api import MedQoLPhysicianCalculator
from .constants_physician import ITEM_OPTIONS, ITEM_QUESTIONS, ITEMS_F1, ITEMS_F2, ITEMS_F3, ITENS_TODOS
from .parameters_physician import load_parameters_physician

try:
    __version__ = version("afya-medqol")
except PackageNotFoundError:  # pragma: no cover - pacote não instalado (execução local)
    __version__ = "0.0.0.dev0"

__all__ = [
    "MedQoLPhysicianCalculator",
    "load_parameters_physician",
    "ITEMS_F1",
    "ITEMS_F2",
    "ITEMS_F3",
    "ITENS_TODOS",
    "ITEM_QUESTIONS",
    "ITEM_OPTIONS",
    "__version__",
]
