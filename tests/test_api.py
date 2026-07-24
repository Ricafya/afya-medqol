import os

import pandas as pd
import pytest

from afya_medqol import MedQoLPhysicianCalculator

DADOS = os.path.join(os.path.dirname(__file__), "data", "respostas_exemplo.csv")


@pytest.fixture(scope="module")
def calc():
    return MedQoLPhysicianCalculator()


def test_item_questions_available_on_instance(calc):
    en = calc.item_questions()
    pt = calc.item_questions(lang="pt")
    assert en["F1_1_enjoymentoflife"] == "28.3. To what extent do you enjoy life?"
    assert pt["F1_1_enjoymentoflife"] == "28.3. O quanto você aproveita a vida?"
    assert set(en.keys()) == set(calc.items)
    assert set(pt.keys()) == set(calc.items)


def test_item_options_available_on_instance(calc):
    en = calc.item_options()
    pt = calc.item_options(lang="pt")
    assert en["F1_1_enjoymentoflife"] == [
        "Not at all (1)", "Very little (2)", "Moderately (3)", "Quite a bit (4)", "Extremely (5)",
    ]
    assert pt["F1_1_enjoymentoflife"] == [
        "Nada (1)", "Muito pouco (2)", "Mais ou menos (3)", "Bastante (4)", "Extremamente (5)",
    ]
    assert set(en.keys()) == set(calc.items)
    assert set(pt.keys()) == set(calc.items)
    for item in calc.items:
        assert len(en[item]) == 5
        assert len(pt[item]) == 5


def test_factor_items(calc):
    assert calc.factor_items == {
        "Factor1": [
            "F1_1_enjoymentoflife", "F1_2_financialsufficiency", "F1_3_accesstoinformation",
            "F1_4_leisureopportunities", "F1_5_mobilitypast2weeks", "F1_6_accesstohealthservices",
        ],
        "Factor2": [
            "F2_1_technicaltraining", "F2_2_mentalhealthsupport",
            "F2_3_coworkersupportnetwork", "F2_4_educationalhandlingoferrors",
        ],
        "Factor3": ["F3_1_stresshurtsperformance", "F3_2_stressledtoerrors", "F3_3_stresshurtsrelationships"],
    }
    assert sum((len(v) for v in calc.factor_items.values()), 0) == len(calc.items)


def test_missing_and_code_999_raise_error(calc):
    df = pd.DataFrame([{
        "id": "resp_com_omissos",
        "F1_1_enjoymentoflife": 4, "F1_2_financialsufficiency": None, "F1_3_accesstoinformation": 4,
        "F1_4_leisureopportunities": 4, "F1_5_mobilitypast2weeks": 3, "F1_6_accesstohealthservices": 4,
        "F2_1_technicaltraining": 999, "F2_2_mentalhealthsupport": 4,
        "F2_3_coworkersupportnetwork": 4, "F2_4_educationalhandlingoferrors": 3,
        "F3_1_stresshurtsperformance": 2, "F3_2_stressledtoerrors": 2, "F3_3_stresshurtsrelationships": 2,
    }])
    with pytest.raises(ValueError, match="F1_2_financialsufficiency") as excinfo:
        calc.score_batch(df)
    assert "F2_1_technicaltraining" in str(excinfo.value)
    assert "resp_com_omissos" in str(excinfo.value)


def test_score_physician_matches_score_batch(calc):
    answers = {
        "F1_1_enjoymentoflife": 4, "F1_2_financialsufficiency": 4, "F1_3_accesstoinformation": 4,
        "F1_4_leisureopportunities": 4, "F1_5_mobilitypast2weeks": 4, "F1_6_accesstohealthservices": 4,
        "F2_1_technicaltraining": 4, "F2_2_mentalhealthsupport": 4,
        "F2_3_coworkersupportnetwork": 4, "F2_4_educationalhandlingoferrors": 4,
        "F3_1_stresshurtsperformance": 2, "F3_2_stressledtoerrors": 2, "F3_3_stresshurtsrelationships": 2,
    }
    unico = calc.score_physician(answers)
    lote = calc.score_batch(pd.DataFrame([answers])).iloc[0]
    assert unico["theta_global"] == pytest.approx(lote["theta_global"])


def test_score_batch_accepts_dataframe_read_from_csv(calc):
    df = pd.read_csv(DADOS)
    out = calc.score_batch(df)
    assert len(out) == 4


def test_score_batch_missing_columns_raises_error(calc):
    df = pd.DataFrame({"F1_1_enjoymentoflife": [3]})
    with pytest.raises(ValueError, match="MedQoLPhysicianCalculator.score_batch"):
        calc.score_batch(df)


def test_value_outside_1_to_5_raises_error(calc):
    answers = {
        "F1_1_enjoymentoflife": 4, "F1_2_financialsufficiency": 4, "F1_3_accesstoinformation": 4,
        "F1_4_leisureopportunities": 4, "F1_5_mobilitypast2weeks": 4, "F1_6_accesstohealthservices": 4,
        "F2_1_technicaltraining": 4, "F2_2_mentalhealthsupport": 4,
        "F2_3_coworkersupportnetwork": 4, "F2_4_educationalhandlingoferrors": 4,
        "F3_1_stresshurtsperformance": 6, "F3_2_stressledtoerrors": 2.5, "F3_3_stresshurtsrelationships": "abc",
    }
    with pytest.raises(ValueError, match="integer from 1 to 5") as excinfo:
        calc.score_physician(answers)
    assert "F3_1_stresshurtsperformance" in str(excinfo.value)
    assert "F3_2_stressledtoerrors" in str(excinfo.value)
    assert "F3_3_stresshurtsrelationships" in str(excinfo.value)


def test_missing_one_item_raises_error_in_score_physician(calc):
    answers_completo = {
        "F1_1_enjoymentoflife": 4, "F1_2_financialsufficiency": 4, "F1_3_accesstoinformation": 4,
        "F1_4_leisureopportunities": 4, "F1_5_mobilitypast2weeks": 4, "F1_6_accesstohealthservices": 4,
        "F2_1_technicaltraining": 4, "F2_2_mentalhealthsupport": 4,
        "F2_3_coworkersupportnetwork": 4, "F2_4_educationalhandlingoferrors": 4,
        "F3_1_stresshurtsperformance": 2, "F3_2_stressledtoerrors": 2, "F3_3_stresshurtsrelationships": 2,
    }
    answers_sem_f1_1 = {k: v for k, v in answers_completo.items() if k != "F1_1_enjoymentoflife"}

    calc.score_physician(answers_completo)
    with pytest.raises(ValueError, match="F1_1_enjoymentoflife"):
        calc.score_physician(answers_sem_f1_1)
