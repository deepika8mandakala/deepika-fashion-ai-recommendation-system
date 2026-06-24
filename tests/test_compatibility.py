from app.compatibility.engine import CompatibilityEngine
from app.models.product import Product


def product(color: str, usage: str, article: str) -> Product:
    return Product("1", f"{color} {article}", "male", "apparel", "topwear", article, color, "summer", usage)


def test_pair_score_rewards_compatible_palette():
    engine = CompatibilityEngine()
    white_shirt = product("white", "formal", "shirt")
    navy_chinos = product("navy", "formal", "chinos")
    assert engine.pair_score(white_shirt, navy_chinos) > 0.8

