"""Response serialization helpers."""

from pathlib import Path

from app.models.product import Outfit, RankedProduct
from app.schemas.recommendation import (
    OutfitResponse,
    ProductResponse,
    ScoreBreakdownResponse,
)

BASE_URL = "https://deepika-fashion-ai-recommendation-system-mvcz.onrender.com"


def to_public_image_url(local_path: str | None) -> str | None:
    """
    Convert local filesystem paths into public URLs
    that FastAPI serves through StaticFiles.
    """

    if not local_path:
        return None

    normalized = local_path.replace("\\", "/")

    if "images/" in normalized:
        relative = normalized.split("images/", 1)[1]
        return f"{BASE_URL}/images/{relative}"

    if "generated_outfits/" in normalized:
        filename = Path(normalized).name
        return f"{BASE_URL}/generated/{filename}"

    return local_path


def ranked_product_to_response(
    item: RankedProduct | None,
) -> ProductResponse | None:
    """
    Serialize ranked product for API/UI.
    """

    if item is None:
        return None

    product = item.product

    return ProductResponse(
        id=product.id,
        name=product.product_display_name,
        category_slot=product.category_slot,
        article_type=product.article_type,
        color=product.base_colour,
        gender=product.gender,
        season=product.season,
        usage=product.usage,
        image_path=to_public_image_url(product.image_path),
        score=item.score,
        breakdown=ScoreBreakdownResponse(
            **item.breakdown.__dict__
        ),
    )


def outfit_to_response(outfit: Outfit) -> OutfitResponse:
    """
    Serialize outfit domain object.
    """

    return OutfitResponse(
        topwear=ranked_product_to_response(outfit.topwear),
        bottomwear=ranked_product_to_response(outfit.bottomwear),
        footwear=ranked_product_to_response(outfit.footwear),
        accessories=[
            item
            for item in (
                ranked_product_to_response(accessory)
                for accessory in outfit.accessories
            )
            if item
        ],
        compatibility_score=outfit.compatibility_score,
        reasoning=outfit.reasoning,
        generated_image_path=to_public_image_url(
            outfit.generated_image_path
        ),
    )
