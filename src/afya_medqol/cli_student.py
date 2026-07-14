"""CLI: ``iqol-estudante respostas.csv [--saida out.csv]``."""

from __future__ import annotations

import argparse

from .api import calcular_indice_estudante


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="iqol-estudante",
        description="Calcula o índice IQoL (estudantes de medicina, GRM bifatorial).",
    )
    parser.add_argument("respostas", help="CSV com as colunas dos 8 itens (F1_1_overallqol, F1_2_satisfactionwithhealth, F1_3_enjoymentoflife, F1_4_perceivedmeaninginlife, F2_1_energyfordailyactivities, F2_2_satisfactionwithsleep, F3_1_performdailyactivities, F3_2_capacityforwork).")
    parser.add_argument("--saida", default=None, help="Caminho do CSV de saída.")
    args = parser.parse_args()

    out = calcular_indice_estudante(args.respostas, args.saida)

    print(f"OK — {len(out)} respondentes processados")
    print("\nT-score global — média ± dp:")
    s = out["T_score_global"].dropna()
    print(f"  T_score_global: {s.mean():.2f} ± {s.std():.2f}")


if __name__ == "__main__":
    main()
