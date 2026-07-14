import numpy as np
import pytest

from afya_medqol.constants_physician import ITENS_TODOS
from afya_medqol.parameters_physician import carregar_parametros


def test_carrega_tabela_embutida():
    par = carregar_parametros()
    assert par["ITENS"] == ITENS_TODOS
    assert par["A"].shape == (13, 3)
    assert par["B"].shape == (13, 4)
    assert par["SIGMA"].shape == (3, 3)
    np.testing.assert_allclose(np.diag(par["SIGMA"]), 1.0)


def test_pesos_somam_um():
    par = carregar_parametros()
    assert par["PESOS"].sum() == pytest.approx(1.0, abs=1e-6)
