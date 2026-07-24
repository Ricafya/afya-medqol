import os

import pandas as pd
import pytest

from afya_medqol import MedQoLStudentCalculator

DADOS = os.path.join(os.path.dirname(__file__), "data", "respostas_estudantes_exemplo.csv")


@pytest.fixture(scope="module")
def calc():
    return MedQoLStudentCalculator()


@pytest.fixture(scope="module")
def df_resultado(calc):
    df = pd.read_csv(DADOS)
    return calc.score_batch(df).set_index("id")


def test_item_questions_available_on_instance(calc):
    en = calc.item_questions()
    pt = calc.item_questions(lang="pt")
    assert en["F1_1_overallqol"] == "22. How would you rate your quality of life?"
    assert pt["F1_1_overallqol"] == "22. Pensando nas duas últimas semanas, como você avaliaria sua qualidade de vida?"
    assert set(en.keys()) == set(calc.items)
    assert set(pt.keys()) == set(calc.items)


def test_item_options_available_on_instance(calc):
    en = calc.item_options()
    pt = calc.item_options(lang="pt")
    assert en["F1_1_overallqol"] == [
        "Very poor (1)", "Poor (2)", "Neither poor nor good (3)", "Good (4)", "Very good (5)",
    ]
    assert pt["F1_1_overallqol"] == [
        "Muito ruim (1)", "Ruim (2)", "Nem ruim, nem boa (3)", "Boa (4)", "Muito boa (5)",
    ]
    assert set(en.keys()) == set(calc.items)
    assert set(pt.keys()) == set(calc.items)
    for item in calc.items:
        assert len(en[item]) == 5
        assert len(pt[item]) == 5


def test_factor_items(calc):
    assert calc.factor_items == {
        "Factor1": [
            "F1_1_overallqol", "F1_2_satisfactionwithhealth",
            "F1_3_enjoymentoflife", "F1_4_perceivedmeaninginlife",
        ],
        "Factor2": ["F2_1_energyfordailyactivities", "F2_2_satisfactionwithsleep"],
        "Factor3": ["F3_1_performdailyactivities", "F3_2_capacityforwork"],
    }
    assert sum((len(v) for v in calc.factor_items.values()), 0) == len(calc.items)


def test_high_respondent_surpasses_low(df_resultado):
    alto = df_resultado.loc["E001", "theta_global"]
    baixo = df_resultado.loc["E002", "theta_global"]
    assert alto > baixo


def test_missing_and_code_999_raise_error(calc):
    df = pd.DataFrame([{
        "id": "E004",
        "F1_1_overallqol": 4, "F1_2_satisfactionwithhealth": None, "F1_3_enjoymentoflife": 4, "F1_4_perceivedmeaninginlife": 3,
        "F2_1_energyfordailyactivities": 999, "F2_2_satisfactionwithsleep": 4, "F3_1_performdailyactivities": 2, "F3_2_capacityforwork": 3,
    }])
    with pytest.raises(ValueError, match="F1_2_satisfactionwithhealth") as excinfo:
        calc.score_batch(df)
    assert "F2_1_energyfordailyactivities" in str(excinfo.value)
    assert "E004" in str(excinfo.value)


def test_matches_reference_script(df_resultado):
    # valores gerados pelo script de referência calcular_indice_IQoL.py
    # (mesmos parâmetros, mesma quadratura fixa) para os respondentes completos E001-E003.
    esperado = {
        "E001": (0.546408, 0.036023, 0.311684, 0.380536),
        "E002": (-1.056184, 0.050283, -0.254782, -0.598458),
        "E003": (-0.617983, 0.019531, -0.081657, -0.329279),
    }
    for resp_id, (t1, t2, t3, tg) in esperado.items():
        row = df_resultado.loc[resp_id]
        assert row["theta1_psychological_well_being"] == pytest.approx(t1, abs=1e-5)
        assert row["theta2_vitality"] == pytest.approx(t2, abs=1e-5)
        assert row["theta3_perceived_functional_capacity"] == pytest.approx(t3, abs=1e-5)
        assert row["theta_global"] == pytest.approx(tg, abs=1e-5)


def test_value_outside_1_to_5_raises_error(calc):
    answers = {
        "F1_1_overallqol": 4, "F1_2_satisfactionwithhealth": 4, "F1_3_enjoymentoflife": 0, "F1_4_perceivedmeaninginlife": 3.5,
        "F2_1_energyfordailyactivities": 3, "F2_2_satisfactionwithsleep": 4, "F3_1_performdailyactivities": 3, "F3_2_capacityforwork": "abc",
    }
    with pytest.raises(ValueError, match="integer from 1 to 5") as excinfo:
        calc.score_student(answers)
    assert "F1_3_enjoymentoflife" in str(excinfo.value)
    assert "F1_4_perceivedmeaninginlife" in str(excinfo.value)
    assert "F3_2_capacityforwork" in str(excinfo.value)


def test_missing_one_item_raises_error_in_score_student(calc):
    answers_completo = {
        "F1_1_overallqol": 4, "F1_2_satisfactionwithhealth": 4, "F1_3_enjoymentoflife": 4, "F1_4_perceivedmeaninginlife": 3,
        "F2_1_energyfordailyactivities": 3, "F2_2_satisfactionwithsleep": 4, "F3_1_performdailyactivities": 3, "F3_2_capacityforwork": 3,
    }
    answers_sem_f1_1 = {k: v for k, v in answers_completo.items() if k != "F1_1_overallqol"}
    answers_sem_f1_todos = {k: v for k, v in answers_completo.items() if not k.startswith("F1_")}

    calc.score_student(answers_completo)
    with pytest.raises(ValueError, match="F1_1_overallqol"):
        calc.score_student(answers_sem_f1_1)
    with pytest.raises(ValueError, match="MedQoLStudentCalculator.score_batch"):
        calc.score_student(answers_sem_f1_todos)


def test_score_student_matches_score_batch(calc):
    answers = {
        "F1_1_overallqol": 4, "F1_2_satisfactionwithhealth": 4, "F1_3_enjoymentoflife": 4, "F1_4_perceivedmeaninginlife": 3,
        "F2_1_energyfordailyactivities": 3, "F2_2_satisfactionwithsleep": 4, "F3_1_performdailyactivities": 3, "F3_2_capacityforwork": 3,
    }
    unico = calc.score_student(answers)
    lote = calc.score_batch(pd.DataFrame([answers])).iloc[0]
    assert unico["theta_global"] == pytest.approx(lote["theta_global"])
    assert "nivel_qv" not in unico
    assert "score_global_centesimal" not in unico


def test_score_batch_accepts_dataframe_read_from_csv(calc):
    df = pd.read_csv(DADOS)
    out = calc.score_batch(df)
    assert len(out) == 4


def test_score_batch_missing_columns_raises_error(calc):
    df = pd.DataFrame({"F1_1_overallqol": [3]})
    with pytest.raises(ValueError, match="MedQoLStudentCalculator.score_batch"):
        calc.score_batch(df)
