"""Explicit outfit compatibility rules and explainable matrices."""

from __future__ import annotations

from app.models.product import Product


STYLE_TO_USAGE = {
    "business": {"formal", "smart casual", "office"},
    "interview": {"formal"},
    "formal": {"formal", "office"},
    "office": {"office", "formal"},
    "casual": {"casual", "smart casual"},
    "party": {"party"},
    "wedding": {"wedding", "festive", "ethnic", "formal", "party"},
    "festive": {"festive", "wedding"},
    "ethnic": {"festive", "wedding"},
    "vacation": {"vacation", "casual", "travel"},
    "beach": {"casual", "beach"},
    "sports": {"sports"},
    "winter": {"winter", "casual", "formal"},
    "summer": {"casual", "formal", "beach"},
    "streetwear": {"casual", "streetwear"},
}

COLOR_COMPATIBILITY = {
    "white": {"navy", "blue", "black", "grey", "brown", "beige"},
    "black": {"grey", "white", "blue", "red", "olive"},
    "navy": {"white", "brown", "beige", "grey"},
    "blue": {"white", "brown", "grey", "black"},
    "grey": {"black", "white", "navy", "blue"},
    "brown": {"white", "navy", "beige", "cream"},
    "beige": {"white", "navy", "brown", "olive"},
    "red": {"black", "white", "blue"},
    "green": {"white", "beige", "brown", "black"},
    "olive": {"black", "white", "beige", "brown"},
}

FOOTWEAR_BY_OCCASION = {
    "business": {"loafer", "formal shoes", "heels"},
    "interview": {"loafer", "formal shoes", "heels"},
    "formal": {"loafer", "formal shoes", "heels"},
    "casual": {"sneakers", "sandals", "casual shoes"},
    "party": {"heels", "sneakers", "boots", "formal shoes"},
    "wedding": {"heels", "formal shoes", "ethnic footwear"},
    "beach": {"sandals", "flip flops"},
    "sports": {"sports shoes", "sneakers"},
}


class CompatibilityEngine:
    """Scores and explains outfit coherence using transparent domain rules."""

    def category_match(self, product: Product, required_slot: str) -> float:
        return 1.0 if product.category_slot == required_slot else 0.35 if product.category_slot != "other" else 0.0

    def occasion_match(self, product: Product, occasion: str | None) -> float:
        if not occasion:
            return 0.6
        normalized = occasion.lower()
        usage_targets = set()
        for key, values in STYLE_TO_USAGE.items():
            if key in normalized:
                usage_targets |= values
        if not usage_targets:
            usage_targets = STYLE_TO_USAGE.get(normalized, {normalized})
        return 1.0 if product.usage in usage_targets else 0.45

    def style_match(self, product: Product, style: str | None) -> float:
        if not style:
            return 0.6
        allowed = STYLE_TO_USAGE.get(style.lower(), {style.lower()})
        normalized = style.lower()
        return 1.0 if (
            product.usage in allowed
            or product.sub_category == normalized
            or normalized in product.semantic_description.lower()
        ) else 0.4

    def color_match(self, product: Product, preferred_colors: list[str]) -> float:
        if not preferred_colors:
            return 0.65
        normalized = {color.lower() for color in preferred_colors}
        return 1.0 if product.base_colour in normalized else 0.45

    def season_match(self, product: Product, season: str | None) -> float:
        if not season:
            return 0.65
        return 1.0 if product.season == season.lower() or product.season == "all season" else 0.4

    def gender_match(self, product: Product, gender: str | None) -> float:
        if not gender or product.gender in {"unisex", "unknown"}:
            return 1.0
        return 1.0 if product.gender == gender.lower() else 0.25

    def pair_score(self, first: Product | None, second: Product | None) -> float:
        """Score color and usage compatibility between two retrieved products."""

        if first is None or second is None:
            return 0.0
        color_ok = second.base_colour in COLOR_COMPATIBILITY.get(first.base_colour, set())
        reverse_ok = first.base_colour in COLOR_COMPATIBILITY.get(second.base_colour, set())
        usage_ok = first.usage == second.usage or "casual" in {first.usage, second.usage}
        return (0.7 if color_ok or reverse_ok else 0.45) + (0.3 if usage_ok else 0.15)

    def outfit_score(self, topwear: Product | None, bottomwear: Product | None, footwear: Product | None) -> float:
        pairs = [
            self.pair_score(topwear, bottomwear),
            self.pair_score(topwear, footwear),
            self.pair_score(bottomwear, footwear),
        ]
        valid = [score for score in pairs if score > 0]
        if not valid:
            return 0.0
        return round(min(1.0, sum(valid) / len(valid)) * 100, 2)

    def explain(self, topwear: Product | None, bottomwear: Product | None, footwear: Product | None) -> list[str]:
        """Generate grounded explanations that reference actual retrieved products."""

        lines: list[str] = []
        if topwear and bottomwear:
            lines.append(
                f"{bottomwear.product_display_name} complements {topwear.product_display_name} "
                f"through a {bottomwear.base_colour} and {topwear.base_colour} palette suitable for {topwear.usage} styling."
            )
        if footwear and topwear:
            lines.append(
                f"{footwear.product_display_name} grounds the outfit while matching the {topwear.usage} intent of "
                f"{topwear.product_display_name}."
            )
        if not lines:
            lines.append("The recommendation is based on retrieved catalog items and explicit category compatibility.")
        return lines
