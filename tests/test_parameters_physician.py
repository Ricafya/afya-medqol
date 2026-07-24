import numpy as np
import pytest

from afya_medqol.constants_physician import ITEM_QUESTIONS, ITENS_TODOS
from afya_medqol.parameters_physician import load_parameters_physician


def test_loads_embedded_table():
    par = load_parameters_physician()
    assert par["ITEMS"] == ITENS_TODOS
    assert par["A"].shape == (13, 3)
    assert par["B"].shape == (13, 4)
    assert par["SIGMA"].shape == (3, 3)
    np.testing.assert_allclose(np.diag(par["SIGMA"]), 1.0)


def test_weights_sum_to_one():
    par = load_parameters_physician()
    assert par["WEIGHTS"].sum() == pytest.approx(1.0, abs=1e-6)


def test_item_questions_covers_all_items_in_both_languages():
    assert set(ITEM_QUESTIONS.keys()) == set(ITENS_TODOS)
    for translations in ITEM_QUESTIONS.values():
        assert set(translations.keys()) == {"en", "pt"}
        assert all(isinstance(text, str) and text for text in translations.values())
