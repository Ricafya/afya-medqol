"""Motor psicométrico bifatorial do IQoL: quadratura 2D, GRM e EAP.

Cada item carrega no fator geral de QV (θ_G, comum aos 8 itens) e no fator
específico do seu domínio (θ_S). Fatores ortogonais, prior N(0,1) em cada
dimensão. O EAP integra θ_G conjuntamente sobre os domínios e, para cada
domínio, integra E[θ_S | θ_G] sobre a posterior marginal de θ_G — o
procedimento clássico de escoragem bifatorial (Gibbons & Hedeker).
"""

from __future__ import annotations

from typing import Any

import numpy as np

from .constants_student import LIMITE_GRID_ESTUDANTE, N_GRID_ESTUDANTE


def build_bifactor_quadrature(n_grid: int = N_GRID_ESTUDANTE, limite: float = LIMITE_GRID_ESTUDANTE):
    """Grade fixa e prior N(0,1) para θ_G e θ_S (mesma grade nas duas dimensões)."""
    grid = np.linspace(-limite, limite, n_grid)
    phi = np.exp(-0.5 * grid**2)
    phi /= phi.sum()
    malha_g, malha_s = np.meshgrid(grid, grid, indexing="ij")
    return grid, phi, malha_g, malha_s


def _probabilidades_item(item: dict[str, Any], malha_g: np.ndarray, malha_s: np.ndarray) -> list[np.ndarray]:
    """P(Y=k | θ_G, θ_S), k=1..5, GRM bifatorial (Samejima) em cada nó da grade."""
    lin = item["aG"] * malha_g + item["aS"] * malha_s
    cum = [1.0 / (1.0 + np.exp(-(lin + dk))) for dk in item["d"]]
    return [1 - cum[0], cum[0] - cum[1], cum[1] - cum[2], cum[2] - cum[3], cum[3]]


def compute_domain_marginals(
    itens: dict[str, dict[str, Any]],
    cods: list[str],
    answers: tuple[int, ...],
    malha_g: np.ndarray,
    malha_s: np.ndarray,
    phi_s: np.ndarray,
    missing_code: int,
) -> tuple[np.ndarray, np.ndarray]:
    """L(θ_G) e M(θ_G) = ∫_S P(respostas|θ_G,θ_S)·φ(θ_S) dθ_S, integrada e ponderada por θ_S."""
    ll = np.zeros_like(malha_g)
    for cod, k in zip(cods, answers):
        if k == missing_code:
            continue
        p = _probabilidades_item(itens[cod], malha_g, malha_s)
        ll += np.log(np.clip(p[k - 1], 1e-300, None))
    Lk = np.exp(ll) * phi_s[None, :]
    L = Lk.sum(axis=1)
    M = (Lk * malha_s).sum(axis=1)
    return L, M


def combine_bifactor_posterior(
    factors: list[int],
    Ls: dict[int, np.ndarray],
    Ms: dict[int, np.ndarray],
    phi_g: np.ndarray,
) -> dict[int, float]:
    """Combina as marginais L/M por domínio na posterior de θ_G e integra os θ_S (EAP)."""
    post_g = phi_g.copy()
    for f in factors:
        post_g = post_g * Ls[f]
    total = post_g.sum()
    if total <= 0 or not np.isfinite(total):
        return {f: np.nan for f in factors}
    post_g = post_g / total

    thetas: dict[int, float] = {}
    for f in factors:
        esperanca_s_dado_g = Ms[f] / np.clip(Ls[f], 1e-300, None)
        thetas[f] = float((post_g * esperanca_s_dado_g).sum())
    return thetas


def eap_bifatorial(
    domains: dict[int, list[str]],
    respostas_por_dominio: dict[int, tuple[int, ...]],
    itens: dict[str, dict[str, Any]],
    phi_g: np.ndarray,
    malha_g: np.ndarray,
    malha_s: np.ndarray,
    phi_s: np.ndarray,
    missing_code: int,
) -> dict[int, float]:
    """EAP dos θ_S específicos (um por domínio) via integração bifatorial."""
    factors = sorted(domains)
    Ls: dict[int, np.ndarray] = {}
    Ms: dict[int, np.ndarray] = {}
    for f in factors:
        Ls[f], Ms[f] = compute_domain_marginals(
            itens, domains[f], respostas_por_dominio[f], malha_g, malha_s, phi_s, missing_code
        )
    return combine_bifactor_posterior(factors, Ls, Ms, phi_g)
