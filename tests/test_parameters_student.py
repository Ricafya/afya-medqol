import pytest

from afya_medqol.constants_student import ITENS_ESTUDANTE
from afya_medqol.parameters_student import carregar_parametros_estudante


def test_carrega_parametros_estudante():
    par = carregar_parametros_estudante()
    assert set(par["ITENS"].keys()) == set(ITENS_ESTUDANTE)
    assert set(par["DOMINIOS"].keys()) == {1, 2, 3}


def test_dominios_cobrem_todos_os_itens():
    par = carregar_parametros_estudante()
    itens_nos_dominios = [item for itens in par["DOMINIOS"].values() for item in itens]
    assert sorted(itens_nos_dominios) == sorted(ITENS_ESTUDANTE)


def test_pesos_somam_aproximadamente_um():
    # pesos publicados no artigo com 3 casas decimais (0.494/0.172/0.335),
    # a soma carrega um resíduo de arredondamento (1.001)
    par = carregar_parametros_estudante()
    assert sum(par["PESOS"].values()) == pytest.approx(1.0, abs=1e-2)


def test_sigma_g_positivo():
    par = carregar_parametros_estudante()
    assert par["SIGMA_G"] > 0
