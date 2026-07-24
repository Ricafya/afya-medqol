"""Public pipeline: scoring via MedQoLPhysicianCalculator and MedQoLStudentCalculator."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .constants_physician import ITEM_OPTIONS, ITEM_QUESTIONS, ITEMS_F1, ITEMS_F2, ITEMS_F3, N_GRID
from .constants_student import (
    ITEM_OPTIONS as ITEM_OPTIONS_ESTUDANTE,
    ITEM_QUESTIONS as ITEM_QUESTIONS_ESTUDANTE,
    GRID_LIMIT_STUDENT,
    MISSING_CODE_STUDENT,
    N_GRID_STUDENT,
)
from .core_physician import build_quadrature, compute_eap, precompute_item_logp
from .core_student import build_bifactor_quadrature, combine_bifactor_posterior, compute_domain_marginals
from .parameters_physician import load_parameters_physician
from .parameters_student import load_parameters_student


def _validate_items(answers: pd.DataFrame, items: list[str], label: str) -> pd.DataFrame:
    """Validate that every item, for every respondent, is an integer from 1 to 5.

    A blank value, an absent item column, or the ``999`` ("not answered")
    code all count as missing. Anything else that is not exactly an integer
    from 1 to 5 (out of range, decimal, non-numeric) counts as invalid. If
    any respondent has a missing or invalid item, raises ``ValueError``
    naming every affected respondent and item; otherwise returns the answers
    as a numeric DataFrame restricted to ``items``.
    """
    raw = answers.reindex(columns=items)
    numeric = raw.apply(pd.to_numeric, errors="coerce")

    is_missing = raw.isna() | (numeric == 999)
    is_invalid = ~is_missing & ~numeric.isin([1, 2, 3, 4, 5])

    if not (is_missing.to_numpy().any() or is_invalid.to_numpy().any()):
        return numeric

    def _scalar(value):
        return value.item() if isinstance(value, np.generic) else value

    id_col = "id" if "id" in answers.columns else None
    details = []
    for pos in range(len(raw)):
        missing_items = [item for item in items if is_missing.iloc[pos][item]]
        invalid_items = [
            f"{item}={_scalar(raw.iloc[pos][item])!r}" for item in items if is_invalid.iloc[pos][item]
        ]
        if not (missing_items or invalid_items):
            continue
        ref = f"id={answers.iloc[pos][id_col]!r}" if id_col else f"index={answers.index[pos]!r}"
        parts = []
        if missing_items:
            parts.append(f"missing {missing_items}")
        if invalid_items:
            parts.append(f"invalid (must be an integer from 1 to 5) {invalid_items}")
        details.append(f"{ref} " + " and ".join(parts))

    raise ValueError(
        f"{label}: every item must be answered with an integer from 1 to 5. " + "; ".join(details)
    )


class MedQoLPhysicianCalculator:
    """Afya MedQoL Physician index calculator (3D GRM, EAP, per-domain linear equating).

    The quadrature grid and per-item log-probabilities are precomputed
    once at construction time — reuse the same instance when scoring
    multiple batches of respondents.
    """

    def __init__(self, n_grid: int = N_GRID):
        self.parameters = load_parameters_physician()
        self.grid, self.prior = build_quadrature(self.parameters["SIGMA"], n_grid)
        self.item_logp = precompute_item_logp(
            self.parameters["A"], self.parameters["B"], self.grid
        )

    @property
    def items(self) -> list[str]:
        return self.parameters["ITEMS"]

    @property
    def factor_items(self) -> dict[str, list[str]]:
        """Item codes grouped by factor: ``{"Factor1": [...], "Factor2": [...], "Factor3": [...]}``."""
        return {"Factor1": ITEMS_F1, "Factor2": ITEMS_F2, "Factor3": ITEMS_F3}

    def item_questions(self, lang: str = "en") -> dict[str, str]:
        """Original questionnaire wording for each item, keyed by item code.

        ``lang`` selects the translation: ``"en"`` (default) or ``"pt"``.
        """
        return {item: translations[lang] for item, translations in ITEM_QUESTIONS.items()}

    def item_options(self, lang: str = "en") -> dict[str, list[str]]:
        """Original response-option wording for each item, keyed by item code.

        Each value is a list of 5 labels ordered from response value 1 to
        5. ``lang`` selects the translation: ``"en"`` (default) or ``"pt"``.
        """
        return {item: options[lang] for item, options in ITEM_OPTIONS.items()}

    def _thetas(self, data: pd.DataFrame) -> np.ndarray:
        thetas = np.full((len(data), 3), np.nan)
        for idx in range(len(data)):
            row = data.iloc[idx].to_numpy(dtype=float)
            thetas[idx] = compute_eap(row, self.item_logp, self.grid, self.prior)
        return thetas

    def score_batch(self, answers: pd.DataFrame) -> pd.DataFrame:
        """Score a DataFrame of respondents and return a new DataFrame with the results.

        ``answers`` must contain all 13 item columns (see
        :data:`afya_medqol.constants_physician.ITENS_TODOS`), each answered
        for every respondent with an integer from 1 to 5. A blank value,
        ``999`` (the "not answered" code), or an entirely missing item
        column all count as an unanswered item; any other value that is not
        exactly an integer from 1 to 5 counts as invalid. If any respondent
        has a missing or invalid item, this raises ``ValueError`` naming
        every affected respondent and item — no scores are computed.
        """
        par = self.parameters
        data = _validate_items(answers, par["ITEMS"], "MedQoLPhysicianCalculator.score_batch")

        thetas = self._thetas(data)

        out = answers.copy()
        out["theta1_quality_of_life"] = thetas[:, 0]
        out["theta2_institutional_support"] = thetas[:, 1]
        out["theta3_perceived_stress"] = thetas[:, 2]

        w = par["WEIGHTS"]
        f3_sign = -1.0 if par["F3_REVERSE_GLOBAL"] else 1.0
        theta_global = w[0] * thetas[:, 0] + w[1] * thetas[:, 1] + f3_sign * w[2] * thetas[:, 2]
        out["theta_global"] = theta_global

        out["T_score_global"] = 50.0 + 10.0 * theta_global

        return out

    def score_physician(self, answers: dict) -> dict:
        """Score a single respondent passed as a ``{item: answer}`` dict."""
        df = pd.DataFrame([answers])
        return self.score_batch(df).iloc[0].to_dict()


class MedQoLStudentCalculator:
    """Afya MedQoL Student index calculator (medical students, 8 items) — bifactor GRM, EAP.

    Reproduces the scoring from Gobbo M Jr et al. (BMJ Open 2026;16:e106371):
    each item loads on a general QoL factor common to all 8 items and on a
    factor specific to its domain (psychological well-being, vitality,
    functional capacity). The 2D quadrature grid is precomputed once at
    construction time — reuse the same instance when scoring multiple
    batches.
    """

    def __init__(self, n_grid: int = N_GRID_STUDENT, limite: float = GRID_LIMIT_STUDENT):
        self.parameters = load_parameters_student()
        self.grid, self.phi, self.mesh_g, self.mesh_s = build_bifactor_quadrature(n_grid, limite)

    @property
    def items(self) -> list[str]:
        return list(self.parameters["ITEMS"].keys())

    @property
    def factor_items(self) -> dict[str, list[str]]:
        """Item codes grouped by factor: ``{"Factor1": [...], "Factor2": [...], "Factor3": [...]}``."""
        domains = self.parameters["DOMAINS"]
        return {f"Factor{f}": domains[f] for f in sorted(domains)}

    def item_questions(self, lang: str = "en") -> dict[str, str]:
        """Original questionnaire wording for each item, keyed by item code.

        ``lang`` selects the translation: ``"en"`` (default) or ``"pt"``.
        """
        return {item: translations[lang] for item, translations in ITEM_QUESTIONS_ESTUDANTE.items()}

    def item_options(self, lang: str = "en") -> dict[str, list[str]]:
        """Original response-option wording for each item, keyed by item code.

        Each value is a list of 5 labels ordered from response value 1 to
        5. ``lang`` selects the translation: ``"en"`` (default) or ``"pt"``.
        """
        return {item: options[lang] for item, options in ITEM_OPTIONS_ESTUDANTE.items()}

    def score_batch(self, answers: pd.DataFrame) -> pd.DataFrame:
        """Score a DataFrame of Afya MedQoL Student respondents and return a new DataFrame.

        ``answers`` must contain all 8 item columns (see
        :data:`afya_medqol.constants_student.STUDENT_ITEMS`), each answered
        for every respondent with an integer from 1 to 5. A blank value,
        ``999`` (the "not answered" code), or an entirely missing item
        column all count as an unanswered item; any other value that is not
        exactly an integer from 1 to 5 counts as invalid. If any respondent
        has a missing or invalid item, this raises ``ValueError`` naming
        every affected respondent and item — no scores are computed.
        """
        par = self.parameters
        data = _validate_items(answers, self.items, "MedQoLStudentCalculator.score_batch").astype(int)
        domains = par["DOMAINS"]
        factors = sorted(domains)

        cache: dict[int, dict[tuple, tuple[np.ndarray, np.ndarray]]] = {f: {} for f in factors}

        def cached_marginals(f: int, domain_answers: tuple[int, ...]):
            if domain_answers not in cache[f]:
                cache[f][domain_answers] = compute_domain_marginals(
                    par["ITEMS"], domains[f], domain_answers,
                    self.mesh_g, self.mesh_s, self.phi, MISSING_CODE_STUDENT,
                )
            return cache[f][domain_answers]

        n = len(data)
        thetas = {f: np.full(n, np.nan) for f in factors}
        theta_global = np.full(n, np.nan)

        for idx in range(n):
            row = data.iloc[idx]
            answers_by_domain = {f: tuple(int(v) for v in row[domains[f]]) for f in factors}

            Ls, Ms = {}, {}
            for f in factors:
                Ls[f], Ms[f] = cached_marginals(f, answers_by_domain[f])

            row_thetas = combine_bifactor_posterior(factors, Ls, Ms, self.phi)
            if np.isnan(row_thetas[factors[0]]):
                continue
            for f in factors:
                thetas[f][idx] = row_thetas[f]
            theta_global[idx] = sum(par["WEIGHTS"][f] * row_thetas[f] for f in factors)

        out = answers.copy()
        name = par["DOMAIN_NAME"]
        for f in factors:
            out[f"theta{f}_{name[f]}"] = thetas[f]
        out["theta_global"] = theta_global

        z_global = (theta_global - par["MU_G"]) / par["SIGMA_G"]
        out["T_score_global"] = 50.0 + 10.0 * z_global

        return out

    def score_student(self, answers: dict) -> dict:
        """Score a single student passed as a ``{item: answer}`` dict."""
        df = pd.DataFrame([answers])
        return self.score_batch(df).iloc[0].to_dict()
