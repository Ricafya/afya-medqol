"""IQoL bifactor psychometric engine: 2D quadrature, GRM, and EAP.

Each item loads on the general QoL factor (θ_G, common to all 8 items) and
on the factor specific to its domain (θ_S). Orthogonal factors, N(0,1)
prior in each dimension. The EAP integrates θ_G jointly over the domains
and, for each domain, integrates E[θ_S | θ_G] over the marginal posterior
of θ_G — the classic bifactor scoring procedure (Gibbons & Hedeker).
"""

from __future__ import annotations

from typing import Any

import numpy as np

from .constants_student import GRID_LIMIT_STUDENT, N_GRID_STUDENT


def build_bifactor_quadrature(n_grid: int = N_GRID_STUDENT, limite: float = GRID_LIMIT_STUDENT):
    """Fixed grid and N(0,1) prior for θ_G and θ_S (same grid in both dimensions)."""
    grid = np.linspace(-limite, limite, n_grid)
    phi = np.exp(-0.5 * grid**2)
    phi /= phi.sum()
    mesh_g, mesh_s = np.meshgrid(grid, grid, indexing="ij")
    return grid, phi, mesh_g, mesh_s


def _item_probabilities(item: dict[str, Any], mesh_g: np.ndarray, mesh_s: np.ndarray) -> list[np.ndarray]:
    """P(Y=k | θ_G, θ_S), k=1..5, bifactor GRM (Samejima) at each grid node."""
    lin = item["aG"] * mesh_g + item["aS"] * mesh_s
    cum = [1.0 / (1.0 + np.exp(-(lin + dk))) for dk in item["d"]]
    return [1 - cum[0], cum[0] - cum[1], cum[1] - cum[2], cum[2] - cum[3], cum[3]]


def compute_domain_marginals(
    items: dict[str, dict[str, Any]],
    codes: list[str],
    answers: tuple[int, ...],
    mesh_g: np.ndarray,
    mesh_s: np.ndarray,
    phi_s: np.ndarray,
    missing_code: int,
) -> tuple[np.ndarray, np.ndarray]:
    """L(θ_G) and M(θ_G) = ∫_S P(answers|θ_G,θ_S)·φ(θ_S) dθ_S, integrated and weighted by θ_S."""
    ll = np.zeros_like(mesh_g)
    for code, k in zip(codes, answers):
        if k == missing_code:
            continue
        p = _item_probabilities(items[code], mesh_g, mesh_s)
        ll += np.log(np.clip(p[k - 1], 1e-300, None))
    Lk = np.exp(ll) * phi_s[None, :]
    L = Lk.sum(axis=1)
    M = (Lk * mesh_s).sum(axis=1)
    return L, M


def combine_bifactor_posterior(
    factors: list[int],
    Ls: dict[int, np.ndarray],
    Ms: dict[int, np.ndarray],
    phi_g: np.ndarray,
) -> dict[int, float]:
    """Combine the per-domain L/M marginals into the θ_G posterior and integrate the θ_S (EAP)."""
    post_g = phi_g.copy()
    for f in factors:
        post_g = post_g * Ls[f]
    total = post_g.sum()
    if total <= 0 or not np.isfinite(total):
        return {f: np.nan for f in factors}
    post_g = post_g / total

    thetas: dict[int, float] = {}
    for f in factors:
        expected_s_given_g = Ms[f] / np.clip(Ls[f], 1e-300, None)
        thetas[f] = float((post_g * expected_s_given_g).sum())
    return thetas


def eap_bifactor(
    domains: dict[int, list[str]],
    domain_answers: dict[int, tuple[int, ...]],
    items: dict[str, dict[str, Any]],
    phi_g: np.ndarray,
    mesh_g: np.ndarray,
    mesh_s: np.ndarray,
    phi_s: np.ndarray,
    missing_code: int,
) -> dict[int, float]:
    """EAP of the specific θ_S (one per domain) via bifactor integration."""
    factors = sorted(domains)
    Ls: dict[int, np.ndarray] = {}
    Ms: dict[int, np.ndarray] = {}
    for f in factors:
        Ls[f], Ms[f] = compute_domain_marginals(
            items, domains[f], domain_answers[f], mesh_g, mesh_s, phi_s, missing_code
        )
    return combine_bifactor_posterior(factors, Ls, Ms, phi_g)
