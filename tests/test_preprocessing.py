import pandas as pd

from app.preprocessing.cleaning import clean_products


def test_clean_products_normalizes_and_deduplicates():
    df = pd.DataFrame(
        [
            {
                "id": 1,
                "gender": "Men",
                "masterCategory": "Apparel",
                "subCategory": "Topwear",
                "articleType": "Shirt",
                "baseColour": "White",
                "season": "Summer",
                "usage": "Formal Wear",
                "productDisplayName": " Shirt ",
            },
            {
                "id": 1,
                "gender": "Men",
                "masterCategory": "Apparel",
                "subCategory": "Topwear",
                "articleType": "Shirt",
                "baseColour": "White",
                "season": "Summer",
                "usage": "Formal Wear",
                "productDisplayName": " Shirt ",
            },
        ]
    )
    cleaned = clean_products(df)
    assert len(cleaned) == 1
    assert cleaned.loc[0, "gender"] == "male"
    assert cleaned.loc[0, "usage"] == "formal"
    assert "semantic_description" in cleaned.columns

