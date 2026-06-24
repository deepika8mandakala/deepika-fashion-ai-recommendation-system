"""Run EDA and save summary/plots."""

from pathlib import Path

import pandas as pd

from app.preprocessing.eda import dataset_summary, save_distribution_plots


def main() -> None:
    input_path = Path("data/raw/styles.csv")
    if not input_path.exists():
        input_path = Path("data/sample_products.csv")
    df = pd.read_csv(input_path)
    summary = dataset_summary(df)
    output_dir = Path("docs/eda")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.md").write_text(
        "\n".join([f"# EDA Summary", f"- Shape: {summary['shape']}", f"- Duplicates: {summary['duplicates']}"]),
        encoding="utf-8",
    )
    save_distribution_plots(df, output_dir)


if __name__ == "__main__":
    main()

