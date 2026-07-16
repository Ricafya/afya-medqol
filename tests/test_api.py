import os

import pandas as pd
import pytest

from afya_medqol import MedQoLCalculator, calculate_index_physician

DADOS = os.path.join(os.path.dirname(__file__), "data", "respostas_exemplo.csv")


@pytest.fixture(scope="module")
def calc():
    return MedQoLCalculator()


@pytest.fixture(scope="module")
def df_resultado(calc):
    df = pd.read_csv(DADOS)
    return calc.score_batch(df).set_index("id")


def test_item_questions_disponivel_na_instancia(calc):
    en = calc.item_questions()
    pt = calc.item_questions(lang="pt")
    assert en["F1_1_enjoymentoflife"] == "28.3. To what extent do you enjoy life?"
    assert pt["F1_1_enjoymentoflife"] == "28.3. O quanto você aproveita a vida?"
    assert set(en.keys()) == set(calc.items)
    assert set(pt.keys()) == set(calc.items)


def test_nao_calcula_score_centesimal(df_resultado):
    for col in (
        "score_F1_centesimal", "score_F2_centesimal",
        "score_F3_centesimal", "score_global_centesimal",
    ):
        assert col not in df_resultado.columns


def test_respondente_bem_estar_supera_critico(df_resultado):
    alto = df_resultado.loc["resp_alto_bem_estar", "theta_global"]
    critico = df_resultado.loc["resp_critico", "theta_global"]
    assert alto > critico


def test_lida_com_omissos_e_codigo_999(df_resultado):
    row = df_resultado.loc["resp_com_omissos"]
    assert pd.notna(row["theta_global"])


def test_score_physician_bate_com_score_batch(calc):
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


def test_score_physician_omite_tscores_por_dominio(calc):
    answers = {
        "F1_1_enjoymentoflife": 4, "F1_2_financialsufficiency": 4, "F1_3_accesstoinformation": 4,
        "F1_4_leisureopportunities": 4, "F1_5_mobilitypast2weeks": 4, "F1_6_accesstohealthservices": 4,
        "F2_1_technicaltraining": 4, "F2_2_mentalhealthsupport": 4,
        "F2_3_coworkersupportnetwork": 4, "F2_4_educationalhandlingoferrors": 4,
        "F3_1_stresshurtsperformance": 2, "F3_2_stressledtoerrors": 2, "F3_3_stresshurtsrelationships": 2,
    }
    unico = calc.score_physician(answers)
    for chave in ("T_score_F1", "T_score_F2", "T_score_F3"):
        assert chave not in unico
    assert "T_score_global" in unico

    lote = calc.score_batch(pd.DataFrame([answers])).iloc[0]
    for chave in ("T_score_F1", "T_score_F2", "T_score_F3"):
        assert chave in lote


def test_calculate_index_physician_aceita_caminho_csv():
    out = calculate_index_physician(DADOS)
    assert len(out) == 4


def test_calculate_index_physician_falta_colunas():
    df = pd.DataFrame({"F1_1_enjoymentoflife": [3]})
    with pytest.raises(ValueError):
        calculate_index_physician(df)
