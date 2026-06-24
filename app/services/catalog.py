"""Catalog loading and sample data bootstrap."""

from __future__ import annotations

from pathlib import Path
import re

import pandas as pd
from PIL import Image

from app.models.product import Product
from app.preprocessing.cleaning import clean_products


SAMPLE_PRODUCTS = [
    ["1001", "male", "apparel", "topwear", "shirt", "white", "summer", "formal", "White Formal Cotton Shirt"],
    ["1002", "male", "apparel", "bottomwear", "chinos", "navy", "summer", "formal", "Navy Slim Fit Chinos"],
    ["1003", "male", "footwear", "shoes", "loafer", "brown", "summer", "formal", "Brown Leather Loafers"],
    ["1004", "female", "apparel", "topwear", "blazer", "black", "winter", "formal", "Black Structured Blazer"],
    ["1005", "female", "apparel", "bottomwear", "trousers", "grey", "winter", "formal", "Grey Tailored Trousers"],
    ["1006", "female", "footwear", "shoes", "heels", "black", "all season", "formal", "Black Block Heels"],
    ["1007", "unisex", "apparel", "topwear", "t-shirt", "black", "summer", "streetwear", "Black Oversized Tee"],
    ["1008", "unisex", "apparel", "bottomwear", "cargo", "grey", "summer", "streetwear", "Grey Utility Cargo Pants"],
    ["1009", "unisex", "footwear", "shoes", "sneakers", "white", "all season", "casual", "White Minimal Sneakers"],
    ["1010", "female", "apparel", "topwear", "kurta", "red", "all season", "ethnic", "Red Embroidered Kurta"],
    ["1011", "female", "apparel", "bottomwear", "skirt", "beige", "all season", "ethnic", "Beige Festive Skirt"],
    ["1012", "male", "apparel", "topwear", "linen shirt", "blue", "summer", "beach", "Blue Linen Vacation Shirt"],
    ["1013", "male", "apparel", "bottomwear", "shorts", "beige", "summer", "beach", "Beige Cotton Shorts"],
    ["1014", "unisex", "footwear", "sandals", "sandals", "brown", "summer", "beach", "Brown Beach Sandals"],
    ["1015", "unisex", "accessories", "bags", "watch", "black", "all season", "formal", "Black Minimal Watch"],
]


def ensure_sample_dataset(path: Path) -> Path:
    """Create a small runnable sample catalog when no dataset is provided."""

    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = [
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
    pd.DataFrame(SAMPLE_PRODUCTS, columns=columns).to_csv(path, index=False)
    return path


def normalize_gender(value: object) -> str:
    cleaned = str(value).strip().lower()
    if cleaned in {"men", "man", "male"}:
        return "male"
    if cleaned in {"women", "woman", "female"}:
        return "female"
    return cleaned or "unisex"


def infer_colour(text: str) -> str:
    colors = [
        "black",
        "white",
        "grey",
        "gray",
        "blue",
        "navy",
        "brown",
        "beige",
        "red",
        "maroon",
        "pink",
        "green",
        "gold",
        "silver",
        "cream",
        "tan",
    ]
    lowered = text.lower()
    for color in colors:
        if re.search(rf"\b{color}\b", lowered):
            return "grey" if color == "gray" else color
    return "unknown"


def load_darex_catalog(dataset_dir: Path) -> list[Product]:
    """Load the user-provided Darex dataset and preserve actual image paths."""

    products_path = dataset_dir / "products.csv"
    if not products_path.exists():
        return []

    df = pd.read_csv(products_path)
    products: list[Product] = []
    for row in df.fillna("").to_dict(orient="records"):
        article_type = str(row.get("category_label") or row.get("category") or "unknown").strip().lower()
        usage = str(row.get("occasion") or "casual").strip().lower()
        wear_type = str(row.get("wear_type") or "unknown").strip().lower()
        image_value = str(row.get("image") or "").strip()
        resolved_image_path = (dataset_dir / image_value).resolve() if image_value else None
        if resolved_image_path is None or not is_valid_image(resolved_image_path):
            continue
        image_path = str(resolved_image_path)
        description = str(row.get("description") or "")
        tags = str(row.get("tags") or "")
        name = str(row.get("name") or "Unnamed product").strip()
        brand = str(row.get("brand") or "").strip()
        colour = infer_colour(" ".join([name, description, tags]))
        semantic_description = (
            f"{name} by {brand}. {description} "
            f"Category: {article_type}. Gender: {row.get('gender')}. "
            f"Wear type: {wear_type}. Occasion: {usage}. Tags: {tags}."
        )
        products.append(
            Product(
                id=str(row["id"]),
                product_display_name=name,
                gender=normalize_gender(row.get("gender")),
                master_category=wear_type if wear_type in {"footwear", "accessory"} else "apparel",
                sub_category=wear_type,
                article_type=article_type,
                base_colour=colour,
                season="all season",
                usage=usage,
                image_path=image_path,
                semantic_description=semantic_description,
            )
        )
    return products


def is_valid_image(path: Path) -> bool:
    """Return true only for product images Pillow can decode."""

    if not path.exists() or not path.is_file():
        return False
    try:
        with Image.open(path) as image:
            image.verify()
        return True
    except Exception:
        return False


def load_catalog(data_path: Path, sample_path: Path, darex_dataset_dir: Path | None = None) -> list[Product]:
    """Load cleaned catalog or bootstrap from sample data."""

    if darex_dataset_dir is not None:
        darex_products = load_darex_catalog(darex_dataset_dir)
        if darex_products:
            return darex_products

    source_path = data_path if data_path.exists() else ensure_sample_dataset(sample_path)
    df = pd.read_csv(source_path)
    cleaned = clean_products(df)
    products = []
    for row in cleaned.to_dict(orient="records"):
        products.append(
            Product(
                id=str(row["id"]),
                product_display_name=row["productDisplayName"],
                gender=row["gender"],
                master_category=row["masterCategory"],
                sub_category=row["subCategory"],
                article_type=row["articleType"],
                base_colour=row["baseColour"],
                season=row["season"],
                usage=row["usage"],
                image_path=row.get("image_path"),
                semantic_description=row["semantic_description"],
            )
        )
    return products
