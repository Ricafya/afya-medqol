import pytest

from afya_medqol.constants_student import ITEM_QUESTIONS, STUDENT_ITEMS
from afya_medqol.parameters_student import load_parameters_student


def test_carrega_parametros_estudante():
    par = load_parameters_student()
    assert set(par["ITEMS"].keys()) == set(STUDENT_ITEMS)
    assert set(par["DOMAINS"].keys()) == {1, 2, 3}


def test_dominios_cobrem_todos_os_itens():
    par = load_parameters_student()
    itens_nos_dominios = [item for itens in par["DOMAINS"].values() for item in itens]
    assert sorted(itens_nos_dominios) == sorted(STUDENT_ITEMS)


def test_pesos_somam_aproximadamente_um():
    # pesos publicados no artigo com 3 casas decimais (0.494/0.172/0.335),
    # a soma carrega um resíduo de arredondamento (1.001)
    par = load_parameters_student()
    assert sum(par["WEIGHTS"].values()) == pytest.approx(1.0, abs=1e-2)


def test_sigma_g_positivo():
    par = load_parameters_student()
    assert par["SIGMA_G"] > 0


def test_item_questions_cobre_todos_os_itens_nos_dois_idiomas():
    assert set(ITEM_QUESTIONS.keys()) == set(STUDENT_ITEMS)
    for translations in ITEM_QUESTIONS.values():
        assert set(translations.keys()) == {"en", "pt"}
        assert all(isinstance(text, str) and text for text in translations.values())
