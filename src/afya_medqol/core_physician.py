"""Psychometric engine: 3D quadrature, GRM probabilities, and EAP scoring."""

from __future__ import annotations

from itertools import product

import numpy as np

from .constants_physician import N_CATEGORIES


def build_quadrature(sigma: np.ndarray, n_grid: int, limite: float = 5.0):
    """Build the 3D quadrature grid and the trivariate normal prior.

    Since Σ is diagonal by construction (independent domains), the
    resulting EAP is equivalent to three independent unidimensional EAPs.
    """
    nodes = np.linspace(-limite, limite, n_grid)
    grid = np.array(list(product(nodes, nodes, nodes)))
    inv_sigma = np.linalg.inv(sigma)
    quad = np.einsum("ij,jk,ik->i", grid, inv_sigma, grid)
    log_prior = -0.5 * quad
    log_prior -= log_prior.max()
    prior = np.exp(log_prior)
    prior /= prior.sum()
    return grid, prior


def precompute_item_logp(A: np.ndarray, B: np.ndarray, grid: np.ndarray) -> np.ndarray:
    """GRM (Samejima) log-probability of each category, per item and grid node."""
    n_itens = A.shape[0]
    n_pts = grid.shape[0]
    K = N_CATEGORIES
    out = np.zeros((n_itens, K, n_pts))
    for i in range(n_itens):
        eta = grid @ A[i]
        a_eff = A[i].sum()
        cum = np.zeros((K + 1, n_pts))
        cum[0] = 1.0
        for k in range(1, K):
            cum[k] = 1.0 / (1.0 + np.exp(-(eta - a_eff * B[i, k - 1])))
        cum[K] = 0.0
        p = cum[:-1] - cum[1:]
        out[i] = np.log(np.clip(p, 1e-300, 1.0))
    return out


def compute_eap(
    answers: np.ndarray, item_logp: np.ndarray, grid: np.ndarray, prior: np.ndarray
) -> np.ndarray:
    """EAP score (θ_F1, θ_F2, θ_F3) of a respondent from raw answers."""
    log_like = np.zeros(grid.shape[0])
    for i, x in enumerate(answers):
        if np.isnan(x):
            continue
        k = int(x) - 1
        if k < 0 or k >= N_CATEGORIES:
            continue
        log_like += item_logp[i, k]
    post = prior * np.exp(log_like - log_like.max())
    total = post.sum()
    if total == 0:
        return np.full(3, np.nan)
    post /= total
    return (post[:, None] * grid).sum(axis=0)
