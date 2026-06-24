"""EDA report generation for fashion datasets."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


DISTRIBUTION_COLUMNS = [
    "gender",
    "season",
    "articleType",
    "masterCategory",
    "usage",
    "baseColour",
]


def dataset_summary(df: pd.DataFrame) -> dict[str, object]:
    """Return interview-friendly EDA summary statistics."""

    return {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing_values": df.isna().sum().to_dict(),
        "duplicates": int(df.duplicated().sum()),
        "unique_counts": df.nunique(dropna=False).to_dict(),
    }


def save_distribution_plots(df: pd.DataFrame, output_dir: Path) -> list[Path]:
    """Persist top-category distribution charts for the EDA notebook/docs."""

    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for column in DISTRIBUTION_COLUMNS:
        if column not in df.columns:
            continue
        counts = df[column].fillna("missing").value_counts().head(15)
        fig, ax = plt.subplots(figsize=(10, 5))
        counts.plot(kind="bar", ax=ax)
        ax.set_title(f"{column} distribution")
        ax.set_xlabel(column)
        ax.set_ylabel("count")
        fig.tight_layout()
        path = output_dir / f"{column}_distribution.png"
        fig.savefig(path)
        plt.close(fig)
        paths.append(path)
    return paths

