import os

import pandas as pd
import pytest

from afya_medqol import MedQoLCalculator, calcular_indice

DADOS = os.path.join(os.path.dirname(__file__), "data", "respostas_exemplo.csv")


@pytest.fixture(scope="module")
def calc():
    return MedQoLCalculator()


@pytest.fixture(scope="module")
def df_resultado(calc):
    df = pd.read_csv(DADOS)
    return calc.calcular(df).set_index("id")


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


def test_score_physician_bate_com_calcular_lote(calc):
    respostas = {
        "F1_1_enjoymentoflife": 4, "F1_2_financialsufficiency": 4, "F1_3_accesstoinformation": 4,
        "F1_4_leisureopportunities": 4, "F1_5_mobilitypast2weeks": 4, "F1_6_accesstohealthservices": 4,
        "F2_1_technicaltraining": 4, "F2_2_mentalhealthsupport": 4,
        "F2_3_coworkersupportnetwork": 4, "F2_4_educationalhandlingoferrors": 4,
        "F3_1_stresshurtsperformance": 2, "F3_2_stressledtoerrors": 2, "F3_3_stresshurtsrelationships": 2,
    }
    unico = calc.score_physician(respostas)
    lote = calc.calcular(pd.DataFrame([respostas])).iloc[0]
    assert unico["theta_global"] == pytest.approx(lote["theta_global"])


def test_score_physician_omite_tscores_por_dominio(calc):
    respostas = {
        "F1_1_enjoymentoflife": 4, "F1_2_financialsufficiency": 4, "F1_3_accesstoinformation": 4,
        "F1_4_leisureopportunities": 4, "F1_5_mobilitypast2weeks": 4, "F1_6_accesstohealthservices": 4,
        "F2_1_technicaltraining": 4, "F2_2_mentalhealthsupport": 4,
        "F2_3_coworkersupportnetwork": 4, "F2_4_educationalhandlingoferrors": 4,
        "F3_1_stresshurtsperformance": 2, "F3_2_stressledtoerrors": 2, "F3_3_stresshurtsrelationships": 2,
    }
    unico = calc.score_physician(respostas)
    for chave in ("T_score_F1", "T_score_F2", "T_score_F3"):
        assert chave not in unico
    assert "T_score_global" in unico

    lote = calc.calcular(pd.DataFrame([respostas])).iloc[0]
    for chave in ("T_score_F1", "T_score_F2", "T_score_F3"):
        assert chave in lote


def test_calcular_indice_com_caminho_csv(tmp_path):
    saida = tmp_path / "saida.csv"
    out = calcular_indice(DADOS, caminho_saida=str(saida))
    assert saida.exists()
    assert len(out) == 4


def test_calcular_indice_falta_colunas():
    df = pd.DataFrame({"F1_1_enjoymentoflife": [3]})
    with pytest.raises(ValueError):
        calcular_indice(df)
