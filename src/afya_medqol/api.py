"""Public pipeline: scoring via MedQoLPhysicianCalculator."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .constants_physician import ITEM_OPTIONS, ITEM_QUESTIONS, ITEMS_F1, ITEMS_F2, ITEMS_F3, N_GRID
from .core_physician import build_quadrature, compute_eap, precompute_item_logp
from .parameters_physician import load_parameters_physician


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
