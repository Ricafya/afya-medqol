"""Pipeline público: escoragem via MedQoLCalculator e IQoLCalculator."""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

from .constants_physician import N_GRID
from .constants_student import LIMITE_GRID_ESTUDANTE, MISSING_CODE_ESTUDANTE, N_GRID_ESTUDANTE
from .core_physician import construir_quadratura, eap_respondente, precomputar_logp_itens
from .core_student import combinar_posterior_bifatorial, construir_quadratura_bifatorial, marginais_dominio
from .parameters_physician import carregar_parametros
from .parameters_student import carregar_parametros_estudante


class MedQoLCalculator:
    """Calculadora do índice Afya MedQoL (GRM 3D, EAP, equating linear per-domain).

    A grade de quadratura e as log-probabilidades por item são
    precomputadas uma única vez na construção, o que torna reutilizar a
    mesma instância para múltiplos lotes de respondentes mais eficiente
    do que chamar :func:`calcular_indice` repetidamente.
    """

    def __init__(self, n_grid: int = N_GRID):
        self.parametros = carregar_parametros()
        self.grid, self.prior = construir_quadratura(self.parametros["SIGMA"], n_grid)
        self.item_logp = precomputar_logp_itens(
            self.parametros["A"], self.parametros["B"], self.grid
        )

    @property
    def itens(self) -> list[str]:
        return self.parametros["ITENS"]

    def _thetas(self, dat: pd.DataFrame) -> np.ndarray:
        thetas = np.full((len(dat), 3), np.nan)
        for idx in range(len(dat)):
            row = dat.iloc[idx].to_numpy(dtype=float)
            if np.all(np.isnan(row)):
                continue
            thetas[idx] = eap_respondente(row, self.item_logp, self.grid, self.prior)
        return thetas

    def calcular(self, respostas: pd.DataFrame) -> pd.DataFrame:
        """Escora um DataFrame de respondentes e retorna um novo DataFrame com os resultados.

        ``respostas`` deve conter, no mínimo, as 13 colunas de itens
        (ver :data:`afya_medqol.constants_physician.ITENS_TODOS`). Valores ausentes ou
        ``999`` (código de "não respondeu") são tratados como omissos.
        """
        par = self.parametros
        faltando = set(par["ITENS"]) - set(respostas.columns)
        if faltando:
            raise ValueError(f"Faltam colunas no DataFrame de respostas: {sorted(faltando)}")

        dat = respostas[par["ITENS"]].apply(pd.to_numeric, errors="coerce").replace(999, np.nan)
        thetas = self._thetas(dat)

        out = respostas.copy()
        out["theta_F1"] = thetas[:, 0]
        out["theta_F2"] = thetas[:, 1]
        out["theta_F3"] = thetas[:, 2]

        w = par["PESOS"]
        sinal_f3 = -1.0 if par["F3_REVERSE_GLOBAL"] else 1.0
        theta_global = w[0] * thetas[:, 0] + w[1] * thetas[:, 1] + sinal_f3 * w[2] * thetas[:, 2]
        out["theta_global"] = theta_global

        out["T_score_F1"] = 50.0 + 10.0 * thetas[:, 0]
        out["T_score_F2"] = 50.0 + 10.0 * thetas[:, 1]
        out["T_score_F3"] = 50.0 + 10.0 * thetas[:, 2]
        out["T_score_global"] = 50.0 + 10.0 * theta_global

        return out

    def score_physician(self, respostas: dict) -> dict:
        """Escora um único respondente passado como dict ``{item: resposta}``.

        Omite ``T_score_F1``, ``T_score_F2`` e ``T_score_F3`` do resultado
        (continuam calculados e disponíveis via :meth:`calcular`).
        """
        df = pd.DataFrame([respostas])
        resultado = self.calcular(df).iloc[0].to_dict()
        for chave in ("T_score_F1", "T_score_F2", "T_score_F3"):
            resultado.pop(chave, None)
        return resultado


def calcular_indice(
    respostas: pd.DataFrame | str,
    caminho_saida: str | None = None,
) -> pd.DataFrame:
    """Função de conveniência equivalente ao script original.

    ``respostas`` pode ser um DataFrame já carregado ou um caminho para
    CSV. Se ``caminho_saida`` for informado (ou ``respostas`` for um
    caminho), o resultado também é salvo em CSV (separador ``;``).
    """
    calc = MedQoLCalculator()

    if isinstance(respostas, str):
        df_resp = pd.read_csv(respostas, sep=None, engine="python")
        if caminho_saida is None:
            base, _ = os.path.splitext(respostas)
            caminho_saida = f"{base}_scores_2024_2.csv"
    else:
        df_resp = respostas

    out = calc.calcular(df_resp)

    if caminho_saida is not None:
        out.to_csv(caminho_saida, index=False, sep=";", encoding="utf-8-sig")

    return out


class IQoLCalculator:
    """Calculadora do IQoL (estudantes de medicina, 8 itens) — GRM bifatorial, EAP.

    Reproduz o escoramento de Gobbo M Jr et al. (BMJ Open 2026;16:e106371):
    cada item carrega num fator geral de QV comum aos 8 itens e num fator
    específico do seu domínio (bem-estar psicológico, vitalidade, capacidade
    funcional). A grade de quadratura 2D é precomputada uma única vez na
    construção — reutilize a mesma instância ao escorar múltiplos lotes.
    """

    def __init__(self, n_grid: int = N_GRID_ESTUDANTE, limite: float = LIMITE_GRID_ESTUDANTE):
        self.parametros = carregar_parametros_estudante()
        self.grid, self.phi, self.malha_g, self.malha_s = construir_quadratura_bifatorial(n_grid, limite)

    @property
    def itens(self) -> list[str]:
        return list(self.parametros["ITENS"].keys())

    def _coagir_respostas(self, respostas: pd.DataFrame) -> pd.DataFrame:
        dat = respostas[self.itens].apply(pd.to_numeric, errors="coerce").round()
        dentro_do_intervalo = (dat >= 1) & (dat <= 5)
        return dat.where(dentro_do_intervalo, MISSING_CODE_ESTUDANTE).astype(int)

    def calcular(self, respostas: pd.DataFrame) -> pd.DataFrame:
        """Escora um DataFrame de respondentes do IQoL e retorna um novo DataFrame.

        ``respostas`` deve conter, no mínimo, as 8 colunas de itens (ver
        :data:`afya_medqol.constants_student.ITENS_ESTUDANTE`). Valores
        ausentes, fora do intervalo 1-5 ou ``999`` são tratados como omissos.
        """
        par = self.parametros
        faltando = set(self.itens) - set(respostas.columns)
        if faltando:
            raise ValueError(f"Faltam colunas no DataFrame de respostas: {sorted(faltando)}")

        dat = self._coagir_respostas(respostas)
        dominios = par["DOMINIOS"]
        fatores = sorted(dominios)

        cache: dict[int, dict[tuple, tuple[np.ndarray, np.ndarray]]] = {f: {} for f in fatores}

        def marginais_cache(f: int, respostas_dominio: tuple[int, ...]):
            if respostas_dominio not in cache[f]:
                cache[f][respostas_dominio] = marginais_dominio(
                    par["ITENS"], dominios[f], respostas_dominio,
                    self.malha_g, self.malha_s, self.phi, MISSING_CODE_ESTUDANTE,
                )
            return cache[f][respostas_dominio]

        n = len(dat)
        thetas = {f: np.full(n, np.nan) for f in fatores}
        theta_global = np.full(n, np.nan)

        for idx in range(n):
            respostas_por_dominio = {
                f: tuple(int(v) for v in dat.iloc[idx][dominios[f]]) for f in fatores
            }
            Ls, Ms = {}, {}
            for f in fatores:
                Ls[f], Ms[f] = marginais_cache(f, respostas_por_dominio[f])

            thetas_linha = combinar_posterior_bifatorial(fatores, Ls, Ms, self.phi)
            if np.isnan(thetas_linha[fatores[0]]):
                continue
            for f in fatores:
                thetas[f][idx] = thetas_linha[f]
            theta_global[idx] = sum(par["PESOS"][f] * thetas_linha[f] for f in fatores)

        out = respostas.copy()
        nome = par["NOME_DOMINIO"]
        for f in fatores:
            out[f"theta_{nome[f]}"] = thetas[f]
        out["theta_global"] = theta_global

        z_global = (theta_global - par["MU_G"]) / par["SIGMA_G"]
        out["T_score_global"] = 50.0 + 10.0 * z_global

        return out

    def score_student(self, respostas: dict) -> dict:
        """Escora um único estudante passado como dict ``{item: resposta}``."""
        df = pd.DataFrame([respostas])
        return self.calcular(df).iloc[0].to_dict()


def calcular_indice_estudante(
    respostas: pd.DataFrame | str,
    caminho_saida: str | None = None,
) -> pd.DataFrame:
    """Função de conveniência para escorar o IQoL (estudantes de medicina).

    ``respostas`` pode ser um DataFrame já carregado ou um caminho para
    CSV. Se ``caminho_saida`` for informado (ou ``respostas`` for um
    caminho), o resultado também é salvo em CSV (separador ``;``).
    """
    calc = IQoLCalculator()

    if isinstance(respostas, str):
        df_resp = pd.read_csv(respostas, sep=None, engine="python")
        if caminho_saida is None:
            base, _ = os.path.splitext(respostas)
            caminho_saida = f"{base}_scores_iqol.csv"
    else:
        df_resp = respostas

    out = calc.calcular(df_resp)

    if caminho_saida is not None:
        out.to_csv(caminho_saida, index=False, sep=";", encoding="utf-8-sig")

    return out
