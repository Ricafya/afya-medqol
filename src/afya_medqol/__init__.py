"""Afya MedQoL — cálculo de índices de qualidade de vida para médicos e estudantes.

Dois instrumentos, calibrações independentes, ambos com escoragem 100%
determinística (quadratura fixa, sem semente):

* **Afya MedQoL** (médicos formados) — Samejima GRM 3D com domínios
  independentes, escoragem EAP, calibração 2024_2 (Gobbo Jr M et al.,
  BMJ Open 2025;15:e102783)::

      from afya_medqol import MedQoLCalculator

      calc = MedQoLCalculator()
      resultado = calc.score_batch(df_respostas)
      resultado_unico = calc.score_physician({"F1_1_enjoymentoflife": 4, ...})
      calc.item_questions()["F1_1_enjoymentoflife"]  # -> texto original (inglês)
      calc.item_questions(lang="pt")["F1_1_enjoymentoflife"]  # -> texto original (português)

* **IQoL** (estudantes de medicina, 8 itens) — GRM bifatorial (fator geral +
  fator específico por domínio), escoragem EAP (Gobbo M Jr et al.,
  BMJ Open 2026;16:e106371)::

      from afya_medqol import IQoLCalculator

      calc = IQoLCalculator()
      resultado = calc.score_batch(df_respostas)
      resultado_unico = calc.score_student({"F1_1_overallqol": 4, ...})
      calc.item_questions()["F1_1_overallqol"]  # -> texto original (inglês)
      calc.item_questions(lang="pt")["F1_1_overallqol"]  # -> texto original (português)
"""

from importlib.metadata import PackageNotFoundError, version

from .api import (
    IQoLCalculator,
    MedQoLCalculator,
    calculate_index_physician,
    calculate_index_student,
)
from .constants_physician import ITEM_QUESTIONS, ITENS_F1, ITENS_F2, ITENS_F3, ITENS_TODOS
from .constants_student import ITEM_QUESTIONS as ITEM_QUESTIONS_ESTUDANTE
from .constants_student import STUDENT_ITEMS
from .parameters_physician import load_parameters_physician
from .parameters_student import load_parameters_student

try:
    __version__ = version("afya-medqol")
except PackageNotFoundError:  # pragma: no cover - pacote não instalado (execução local)
    __version__ = "0.0.0.dev0"

__all__ = [
    "MedQoLCalculator",
    "calculate_index_physician",
    "load_parameters_physician",
    "ITENS_F1",
    "ITENS_F2",
    "ITENS_F3",
    "ITENS_TODOS",
    "ITEM_QUESTIONS",
    "IQoLCalculator",
    "calculate_index_student",
    "load_parameters_student",
    "STUDENT_ITEMS",
    "ITEM_QUESTIONS_ESTUDANTE",
    "__version__",
]
