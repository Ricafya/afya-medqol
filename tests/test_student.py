import os

import pandas as pd
import pytest

from afya_medqol import IQoLCalculator, calculate_index_student

DADOS = os.path.join(os.path.dirname(__file__), "data", "respostas_estudantes_exemplo.csv")


@pytest.fixture(scope="module")
def calc():
    return IQoLCalculator()


@pytest.fixture(scope="module")
def df_resultado(calc):
    df = pd.read_csv(DADOS)
    return calc.score_batch(df).set_index("id")


def test_item_questions_disponivel_na_instancia(calc):
    en = calc.item_questions()
    pt = calc.item_questions(lang="pt")
    assert en["F1_1_overallqol"] == "22. How would you rate your quality of life?"
    assert pt["F1_1_overallqol"] == "22. Pensando nas duas últimas semanas, como você avaliaria sua qualidade de vida?"
    assert set(en.keys()) == set(calc.itens)
    assert set(pt.keys()) == set(calc.itens)


def test_nao_calcula_score_centesimal(df_resultado):
    for col in (
        "score_bem_estar_psicologico_centesimal", "score_vitalidade_centesimal",
        "score_capacidade_funcional_centesimal", "score_global_centesimal",
    ):
        assert col not in df_resultado.columns


def test_respondente_alto_supera_baixo(df_resultado):
    alto = df_resultado.loc["E001", "theta_global"]
    baixo = df_resultado.loc["E002", "theta_global"]
    assert alto > baixo


def test_nao_calcula_nivel_qv(df_resultado):
    assert "nivel_qv" not in df_resultado.columns


def test_lida_com_omissos_e_codigo_999(df_resultado):
    row = df_resultado.loc["E004"]
    assert pd.notna(row["theta_global"])


def test_bate_com_script_de_referencia(df_resultado):
    # valores gerados pelo script de referência calcular_indice_IQoL.py
    # (mesmos parâmetros, mesma quadratura fixa) para os respondentes E001-E004
    esperado = {
        "E001": (0.546408, 0.036023, 0.311684, 0.380536),
        "E002": (-1.056184, 0.050283, -0.254782, -0.598458),
        "E003": (-0.617983, 0.019531, -0.081657, -0.329279),
        "E004": (0.312209, 0.514172, -0.878319, -0.051568),
    }
    for resp_id, (t1, t2, t3, tg) in esperado.items():
        row = df_resultado.loc[resp_id]
        assert row["theta1_psychological_well_being"] == pytest.approx(t1, abs=1e-5)
        assert row["theta2_vitality"] == pytest.approx(t2, abs=1e-5)
        assert row["theta3_perceived_functional_capacity"] == pytest.approx(t3, abs=1e-5)
        assert row["theta_global"] == pytest.approx(tg, abs=1e-5)


def test_score_student_bate_com_score_batch(calc):
    answers = {
        "F1_1_overallqol": 4, "F1_2_satisfactionwithhealth": 4, "F1_3_enjoymentoflife": 4, "F1_4_perceivedmeaninginlife": 3,
        "F2_1_energyfordailyactivities": 3, "F2_2_satisfactionwithsleep": 4, "F3_1_performdailyactivities": 3, "F3_2_capacityforwork": 3,
    }
    unico = calc.score_student(answers)
    lote = calc.score_batch(pd.DataFrame([answers])).iloc[0]
    assert unico["theta_global"] == pytest.approx(lote["theta_global"])
    assert "nivel_qv" not in unico
    assert "score_global_centesimal" not in unico


def test_calculate_index_student_com_caminho_csv(tmp_path):
    saida = tmp_path / "saida.csv"
    out = calculate_index_student(DADOS, caminho_saida=str(saida))
    assert saida.exists()
    assert len(out) == 4


def test_calculate_index_student_falta_colunas():
    df = pd.DataFrame({"F1_1_overallqol": [3]})
    with pytest.raises(ValueError):
        calculate_index_student(df)
