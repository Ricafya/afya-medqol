"""CLI: ``afya-medqol answers.csv [--saida out.csv]``."""

from __future__ import annotations

import argparse

from .api import calculate_index_physician


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="afya-medqol",
        description="Calcula o índice Afya MedQoL (calibração 2024_2, régua independente por domínio).",
    )
    parser.add_argument("answers", help="CSV com as colunas dos 13 itens.")
    parser.add_argument("--saida", default=None, help="Caminho do CSV de saída.")
    args = parser.parse_args()

    out = calculate_index_physician(args.answers, args.saida)

    print(f"OK — {len(out)} respondentes processados")
    print("\nT-score — média ± dp:")
    for col in ("T_score_F1", "T_score_F2", "T_score_F3", "T_score_global"):
        s = out[col].dropna()
        print(f"  {col}: {s.mean():.2f} ± {s.std():.2f}")


if __name__ == "__main__":
    main()
