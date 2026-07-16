"""Public pipeline: scoring via MedQoLCalculator and IQoLCalculator."""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

from .constants_physician import ITEM_QUESTIONS, N_GRID
from .constants_student import (
    ITEM_QUESTIONS as ITEM_QUESTIONS_ESTUDANTE,
    LIMITE_GRID_ESTUDANTE,
    MISSING_CODE_ESTUDANTE,
    N_GRID_ESTUDANTE,
)
from .core_physician import build_quadrature, compute_eap, precompute_item_logp
from .core_student import build_bifactor_quadrature, combine_bifactor_posterior, compute_domain_marginals
from .parameters_physician import load_parameters_physician
from .parameters_student import load_parameters_student


class MedQoLCalculator:
    """Afya MedQoL index calculator (3D GRM, EAP, per-domain linear equating).

    The quadrature grid and per-item log-probabilities are precomputed
    once at construction time, which makes reusing the same instance
    for multiple batches of respondents more efficient than calling
    :func:`calculate_index_physician` repeatedly.
    """

    def __init__(self, n_grid: int = N_GRID):
        self.parameters = load_parameters_physician()
        self.grid, self.prior = build_quadrature(self.parameters["SIGMA"], n_grid)
        self.item_logp = precompute_item_logp(
            self.parameters["A"], self.parameters["B"], self.grid
        )

    @property
    def itens(self) -> list[str]:
        return self.parameters["ITEMS"]

    def item_questions(self, lang: str = "en") -> dict[str, str]:
        """Original questionnaire wording for each item, keyed by item code.

        ``lang`` selects the translation: ``"en"`` (default) or ``"pt"``.
        """
        return {item: translations[lang] for item, translations in ITEM_QUESTIONS.items()}

    def _thetas(self, dat: pd.DataFrame) -> np.ndarray:
        thetas = np.full((len(dat), 3), np.nan)
        for idx in range(len(dat)):
            row = dat.iloc[idx].to_numpy(dtype=float)
            if np.all(np.isnan(row)):
                continue
            thetas[idx] = compute_eap(row, self.item_logp, self.grid, self.prior)
        return thetas

    def score_batch(self, answers: pd.DataFrame) -> pd.DataFrame:
        """Score a DataFrame of respondents and return a new DataFrame with the results.

        ``answers`` must contain, at minimum, the 13 item columns
        (see :data:`afya_medqol.constants_physician.ITENS_TODOS`). Missing values or
        ``999`` (the "not answered" code) are treated as missing.
        """
        par = self.parameters
        missing_columns = set(par["ITEMS"]) - set(answers.columns)
        if missing_columns:
            raise ValueError(f"Missing columns in the answers DataFrame: {sorted(missing_columns)}")

        dat = answers[par["ITEMS"]].apply(pd.to_numeric, errors="coerce").replace(999, np.nan)
        thetas = self._thetas(dat)

        out = answers.copy()
        out["theta1_quality_of_life"] = thetas[:, 0]
        out["theta2_institutional_support"] = thetas[:, 1]
        out["theta3_perceived_stress"] = thetas[:, 2]

        w = par["WEIGHTS"]
        sinal_f3 = -1.0 if par["F3_REVERSE_GLOBAL"] else 1.0
        theta_global = w[0] * thetas[:, 0] + w[1] * thetas[:, 1] + sinal_f3 * w[2] * thetas[:, 2]
        out["theta_global"] = theta_global

        out["T_score_F1"] = 50.0 + 10.0 * thetas[:, 0]
        out["T_score_F2"] = 50.0 + 10.0 * thetas[:, 1]
        out["T_score_F3"] = 50.0 + 10.0 * thetas[:, 2]
        out["T_score_global"] = 50.0 + 10.0 * theta_global

        return out

    def score_physician(self, answers: dict) -> dict:
        """Score a single respondent passed as a ``{item: answer}`` dict.

        Omits ``T_score_F1``, ``T_score_F2``, and ``T_score_F3`` from the
        result (they remain computed and available via :meth:`score_batch`).
        """
        df = pd.DataFrame([answers])
        resultado = self.score_batch(df).iloc[0].to_dict()
        for chave in ("T_score_F1", "T_score_F2", "T_score_F3"):
            resultado.pop(chave, None)
        return resultado


def calculate_index_physician(
    answers: pd.DataFrame | str,
    caminho_saida: str | None = None,
) -> pd.DataFrame:
    """Convenience function equivalent to the original script.

    ``answers`` can be an already-loaded DataFrame or a path to a
    CSV file. If ``caminho_saida`` is given (or ``answers`` is a
    path), the result is also saved to CSV (``;``-separated).
    """
    calc = MedQoLCalculator()

    if isinstance(answers, str):
        df_resp = pd.read_csv(answers, sep=None, engine="python")
        if caminho_saida is None:
            base, _ = os.path.splitext(answers)
            caminho_saida = f"{base}_scores_2024_2.csv"
    else:
        df_resp = answers

    out = calc.score_batch(df_resp)

    if caminho_saida is not None:
        out.to_csv(caminho_saida, index=False, sep=";", encoding="utf-8-sig")

    return out


class IQoLCalculator:
    """IQoL index calculator (medical students, 8 items) — bifactor GRM, EAP.

    Reproduces the scoring from Gobbo M Jr et al. (BMJ Open 2026;16:e106371):
    each item loads on a general QoL factor common to all 8 items and on a
    factor specific to its domain (psychological well-being, vitality,
    functional capacity). The 2D quadrature grid is precomputed once at
    construction time — reuse the same instance when scoring multiple
    batches.
    """

    def __init__(self, n_grid: int = N_GRID_ESTUDANTE, limite: float = LIMITE_GRID_ESTUDANTE):
        self.parameters = load_parameters_student()
        self.grid, self.phi, self.malha_g, self.malha_s = build_bifactor_quadrature(n_grid, limite)

    @property
    def itens(self) -> list[str]:
        return list(self.parameters["ITEMS"].keys())

    def item_questions(self, lang: str = "en") -> dict[str, str]:
        """Original questionnaire wording for each item, keyed by item code.

        ``lang`` selects the translation: ``"en"`` (default) or ``"pt"``.
        """
        return {item: translations[lang] for item, translations in ITEM_QUESTIONS_ESTUDANTE.items()}

    def _coerce_answers(self, answers: pd.DataFrame) -> pd.DataFrame:
        dat = answers[self.itens].apply(pd.to_numeric, errors="coerce").round()
        dentro_do_intervalo = (dat >= 1) & (dat <= 5)
        return dat.where(dentro_do_intervalo, MISSING_CODE_ESTUDANTE).astype(int)

    def score_batch(self, answers: pd.DataFrame) -> pd.DataFrame:
        """Score a DataFrame of IQoL respondents and return a new DataFrame.

        ``answers`` must contain, at minimum, the 8 item columns (see
        :data:`afya_medqol.constants_student.STUDENT_ITEMS`). Missing
        values, values outside the 1-5 range, or ``999`` are treated as missing.
        """
        par = self.parameters
        missing_columns = set(self.itens) - set(answers.columns)
        if missing_columns:
            raise ValueError(f"Missing columns in the answers DataFrame: {sorted(missing_columns)}")

        dat = self._coerce_answers(answers)
        domains = par["DOMAINS"]
        factors = sorted(domains)

        cache: dict[int, dict[tuple, tuple[np.ndarray, np.ndarray]]] = {f: {} for f in factors}

        def cached_marginals(f: int, respostas_dominio: tuple[int, ...]):
            if respostas_dominio not in cache[f]:
                cache[f][respostas_dominio] = compute_domain_marginals(
                    par["ITEMS"], domains[f], respostas_dominio,
                    self.malha_g, self.malha_s, self.phi, MISSING_CODE_ESTUDANTE,
                )
            return cache[f][respostas_dominio]

        n = len(dat)
        thetas = {f: np.full(n, np.nan) for f in factors}
        theta_global = np.full(n, np.nan)

        for idx in range(n):
            respostas_por_dominio = {
                f: tuple(int(v) for v in dat.iloc[idx][domains[f]]) for f in factors
            }
            Ls, Ms = {}, {}
            for f in factors:
                Ls[f], Ms[f] = cached_marginals(f, respostas_por_dominio[f])

            thetas_linha = combine_bifactor_posterior(factors, Ls, Ms, self.phi)
            if np.isnan(thetas_linha[factors[0]]):
                continue
            for f in factors:
                thetas[f][idx] = thetas_linha[f]
            theta_global[idx] = sum(par["WEIGHTS"][f] * thetas_linha[f] for f in factors)

        out = answers.copy()
        nome = par["DOMAIN_NAME"]
        for f in factors:
            out[f"theta{f}_{nome[f]}"] = thetas[f]
        out["theta_global"] = theta_global

        z_global = (theta_global - par["MU_G"]) / par["SIGMA_G"]
        out["T_score_global"] = 50.0 + 10.0 * z_global

        return out

    def score_student(self, answers: dict) -> dict:
        """Score a single student passed as a ``{item: answer}`` dict."""
        df = pd.DataFrame([answers])
        return self.score_batch(df).iloc[0].to_dict()


def calculate_index_student(
    answers: pd.DataFrame | str,
    caminho_saida: str | None = None,
) -> pd.DataFrame:
    """Convenience function to score the IQoL (medical students).

    ``answers`` can be an already-loaded DataFrame or a path to a
    CSV file. If ``caminho_saida`` is given (or ``answers`` is a
    path), the result is also saved to CSV (``;``-separated).
    """
    calc = IQoLCalculator()

    if isinstance(answers, str):
        df_resp = pd.read_csv(answers, sep=None, engine="python")
        if caminho_saida is None:
            base, _ = os.path.splitext(answers)
            caminho_saida = f"{base}_scores_iqol.csv"
    else:
        df_resp = answers

    out = calc.score_batch(df_resp)

    if caminho_saida is not None:
        out.to_csv(caminho_saida, index=False, sep=";", encoding="utf-8-sig")

    return out
