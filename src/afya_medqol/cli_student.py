"""CLI: ``iqol-estudante answers.csv [--saida out.csv]``."""

from __future__ import annotations

import argparse
import os

import pandas as pd

from .api import MedQoLStudentCalculator


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="iqol-estudante",
        description="Calcula o índice Afya MedQoL Student (estudantes de medicina, GRM bifatorial).",
    )
    parser.add_argument("answers", help="CSV com as colunas dos 8 itens (F1_1_overallqol, F1_2_satisfactionwithhealth, F1_3_enjoymentoflife, F1_4_perceivedmeaninginlife, F2_1_energyfordailyactivities, F2_2_satisfactionwithsleep, F3_1_performdailyactivities, F3_2_capacityforwork).")
    parser.add_argument("--saida", default=None, help="Caminho do CSV de saída.")
    args = parser.parse_args()

    df_answers = pd.read_csv(args.answers, sep=None, engine="python")
    out = MedQoLStudentCalculator().score_batch(df_answers)

    output_path = args.saida
    if output_path is None:
        base, _ = os.path.splitext(args.answers)
        output_path = f"{base}_scores_iqol.csv"
    out.to_csv(output_path, index=False, sep=";", encoding="utf-8-sig")

    print(f"OK — {len(out)} respondentes processados")
    print(f"Resultado salvo em: {output_path}")
    print("\nT-score global — média ± dp:")
    s = out["T_score_global"].dropna()
    print(f"  T_score_global: {s.mean():.2f} ± {s.std():.2f}")


if __name__ == "__main__":
    main()
