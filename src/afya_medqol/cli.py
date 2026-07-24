"""CLI: ``afya-medqol answers.csv [--saida out.csv]``."""

from __future__ import annotations

import argparse
import os

import pandas as pd

from .api import MedQoLPhysicianCalculator


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="afya-medqol",
        description="Calcula o índice Afya MedQoL Physician (calibração 2024_2, régua independente por domínio).",
    )
    parser.add_argument("answers", help="CSV com as colunas dos 13 itens.")
    parser.add_argument("--saida", default=None, help="Caminho do CSV de saída.")
    args = parser.parse_args()

    df_answers = pd.read_csv(args.answers, sep=None, engine="python")
    out = MedQoLPhysicianCalculator().score_batch(df_answers)

    output_path = args.saida
    if output_path is None:
        base, _ = os.path.splitext(args.answers)
        output_path = f"{base}_scores_2024_2.csv"
    out.to_csv(output_path, index=False, sep=";", encoding="utf-8-sig")

    print(f"OK — {len(out)} respondentes processados")
    print(f"Resultado salvo em: {output_path}")
    s = out["T_score_global"].dropna()
    print(f"\nT_score_global — média ± dp: {s.mean():.2f} ± {s.std():.2f}")


if __name__ == "__main__":
    main()
