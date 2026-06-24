"""Hybrid ranking engine with explicit score contributions."""

from __future__ import annotations

from app.compatibility.engine import CompatibilityEngine
from app.models.product import Product, RankedProduct, ScoreBreakdown
from app.schemas.recommendation import UserIntent


class HybridRanker:
    """Rank retrieved products using retrieval scores plus personalization signals."""

    def __init__(self, compatibility: CompatibilityEngine | None = None) -> None:
        self.compatibility = compatibility or CompatibilityEngine()

    def rank(
        self,
        candidates: list[tuple[Product, float, float]],
        intent: UserIntent,
        required_slot: str,
    ) -> list[RankedProduct]:
        """Rank candidate products for one outfit slot."""

        ranked: list[RankedProduct] = []
        for product, image_similarity, metadata_similarity in candidates:
            if intent.gender and product.gender not in {intent.gender.lower(), "unisex", "unknown"}:
                continue
            gender_multiplier = self.compatibility.gender_match(product, intent.gender)
            breakdown = ScoreBreakdown(
                image_similarity=max(0.0, image_similarity) * gender_multiplier,
                metadata_similarity=max(0.0, metadata_similarity),
                category_match=self.compatibility.category_match(product, required_slot),
                occasion_match=self.compatibility.occasion_match(product, intent.occasion),
                style_match=self.compatibility.style_match(product, intent.preferred_style),
                color_match=self.compatibility.color_match(product, intent.preferred_colors),
                season_match=self.compatibility.season_match(product, intent.season),
            )
            ranked.append(RankedProduct(product=product, score=breakdown.final_score(), breakdown=breakdown))
        return sorted(ranked, key=lambda item: item.score, reverse=True)
