"""Domain models for fashion products and outfits."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Product:
    """Clean, typed representation of one catalog item."""

    id: str
    product_display_name: str
    gender: str
    master_category: str
    sub_category: str
    article_type: str
    base_colour: str
    season: str
    usage: str
    image_path: str | None = None
    semantic_description: str = ""

    @property
    def category_slot(self) -> str:
        """Map noisy article metadata into outfit slots."""

        article = self.article_type.lower()
        sub_category = self.sub_category.lower()
        if any(term in article for term in ("shirt", "t-shirt", "top", "kurta", "blazer", "jacket")):
            return "topwear"
        if any(
            term in article
            for term in ("dress", "saree", "suit", "sherwani", "co ord", "co-ord", "coat", "sweater", "sweatshirt")
        ):
            return "topwear"
        if any(term in article for term in ("jeans", "trouser", "chinos", "shorts", "skirt", "leggings")):
            return "bottomwear"
        if any(term in article for term in ("shoe", "sneaker", "loafer", "sandal", "boot", "heel")):
            return "footwear"
        if self.master_category.lower() == "accessory" or "accessories" in sub_category or any(
            term in article for term in ("watch", "belt", "bag", "tie", "clutch", "necklace", "earring", "sunglass", "cap")
        ):
            return "accessory"
        return "other"

    @property
    def is_one_piece(self) -> bool:
        """Return true for items that already cover the main body outfit."""

        article = self.article_type.lower()
        return any(
            term in article
            for term in ("dress", "saree", "suit", "sherwani", "co ord", "co-ord", "kurta set", "salwar suit")
        )


@dataclass
class ScoreBreakdown:
    """Weighted score components used for ranking and interview defense."""

    image_similarity: float
    metadata_similarity: float
    category_match: float
    occasion_match: float
    style_match: float
    color_match: float
    season_match: float

    def final_score(self) -> float:
        """Compute normalized 0-100 final score from explicit weights."""

        weighted = (
            0.45 * self.image_similarity
            + 0.25 * self.metadata_similarity
            + 0.10 * self.category_match
            + 0.08 * self.occasion_match
            + 0.05 * self.style_match
            + 0.04 * self.color_match
            + 0.03 * self.season_match
        )
        return round(max(0.0, min(1.0, weighted)) * 100, 2)


@dataclass
class RankedProduct:
    """Product plus ranking signals."""

    product: Product
    score: float
    breakdown: ScoreBreakdown


@dataclass
class Outfit:
    """Recommended outfit bundle."""

    topwear: RankedProduct | None
    bottomwear: RankedProduct | None
    footwear: RankedProduct | None
    accessories: list[RankedProduct] = field(default_factory=list)
    compatibility_score: float = 0.0
    reasoning: list[str] = field(default_factory=list)
    generated_image_path: str | None = None
