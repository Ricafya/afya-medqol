"""Afya MedQoL — cálculo de índices de qualidade de vida para médicos e estudantes.

Dois instrumentos, calibrações independentes, ambos com escoragem 100%
determinística (quadratura fixa, sem semente):

* **Afya MedQoL** (médicos formados) — Samejima GRM 3D com domínios
  independentes, escoragem EAP, calibração 2024_2 (Gobbo Jr M et al.,
  BMJ Open 2025;15:e102783)::

      from afya_medqol import MedQoLCalculator

      calc = MedQoLCalculator()
      resultado = calc.calcular(df_respostas)
      resultado_unico = calc.score_physician({"F1_1_enjoymentoflife": 4, ...})

* **IQoL** (estudantes de medicina, 8 itens) — GRM bifatorial (fator geral +
  fator específico por domínio), escoragem EAP (Gobbo M Jr et al.,
  BMJ Open 2026;16:e106371)::

      from afya_medqol import IQoLCalculator

      calc = IQoLCalculator()
      resultado = calc.calcular(df_respostas)
      resultado_unico = calc.score_student({"F1_1_overallqol": 4, ...})
"""

from importlib.metadata import PackageNotFoundError, version

from .api import (
    IQoLCalculator,
    MedQoLCalculator,
    calcular_indice,
    calcular_indice_estudante,
)
from .constants_physician import ITENS_F1, ITENS_F2, ITENS_F3, ITENS_TODOS
from .constants_student import ITENS_ESTUDANTE
from .parameters_physician import carregar_parametros
from .parameters_student import carregar_parametros_estudante

try:
    __version__ = version("afya-medqol")
except PackageNotFoundError:  # pragma: no cover - pacote não instalado (execução local)
    __version__ = "0.0.0.dev0"

__all__ = [
    "MedQoLCalculator",
    "calcular_indice",
    "carregar_parametros",
    "ITENS_F1",
    "ITENS_F2",
    "ITENS_F3",
    "ITENS_TODOS",
    "IQoLCalculator",
    "calcular_indice_estudante",
    "carregar_parametros_estudante",
    "ITENS_ESTUDANTE",
    "__version__",
]
