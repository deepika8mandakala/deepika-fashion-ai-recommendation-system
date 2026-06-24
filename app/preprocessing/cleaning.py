"""Dataset cleaning and semantic description utilities."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
    "id",
    "gender",
    "masterCategory",
    "subCategory",
    "articleType",
    "baseColour",
    "season",
    "usage",
    "productDisplayName",
]


NORMALIZATION_MAPS: dict[str, dict[str, str]] = {
    "gender": {"men": "male", "man": "male", "women": "female", "woman": "female"},
    "season": {"fall": "autumn", "spring/summer": "summer"},
    "usage": {"formal wear": "formal", "office": "formal", "partywear": "party"},
}


def normalize_value(value: object, column: str) -> str:
    """Normalize categorical values while preserving unknowns."""

    if pd.isna(value):
        return "unknown"
    cleaned = str(value).strip().lower().replace("_", " ")
    return NORMALIZATION_MAPS.get(column, {}).get(cleaned, cleaned)


def build_semantic_description(row: pd.Series) -> str:
    """Create metadata text used by sentence-transformer embeddings."""

    return (
        f"{row['productDisplayName']} is a {row['baseColour']} {row['articleType']} "
        f"for {row['gender']} in {row['season']} season, suitable for {row['usage']} use. "
        f"It belongs to {row['masterCategory']} / {row['subCategory']}."
    )


def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    """Clean raw fashion catalog rows into a stable model-ready dataframe."""

    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    cleaned = df.copy()
    cleaned = cleaned.drop_duplicates(subset=["id"]).reset_index(drop=True)
    for column in REQUIRED_COLUMNS:
        if column == "id":
            cleaned[column] = cleaned[column].astype(str)
        elif column == "productDisplayName":
            cleaned[column] = cleaned[column].fillna("Unnamed product").astype(str).str.strip()
        else:
            cleaned[column] = cleaned[column].map(lambda value: normalize_value(value, column))

    cleaned["semantic_description"] = cleaned.apply(build_semantic_description, axis=1)
    return cleaned


def load_and_clean(input_path: Path, output_path: Path) -> pd.DataFrame:
    """Load a CSV, clean it, and persist the processed dataset."""

    raw_df = pd.read_csv(input_path)
    cleaned = clean_products(raw_df)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(output_path, index=False)
    return cleaned

