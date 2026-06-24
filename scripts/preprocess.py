"""Clean raw fashion dataset."""

from pathlib import Path

from app.preprocessing.cleaning import load_and_clean


if __name__ == "__main__":
    load_and_clean(Path("data/raw/styles.csv"), Path("data/processed/products_clean.csv"))

