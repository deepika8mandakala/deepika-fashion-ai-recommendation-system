"""Request and response schemas for recommendation APIs."""

from pydantic import BaseModel, Field


class UserIntent(BaseModel):
    """Structured user intent extracted from natural language or profile fields."""

    occasion: str = Field(default="casual")
    gender: str | None = None
    age: int | None = Field(default=None, ge=1, le=100)
    preferred_colors: list[str] = Field(default_factory=list)
    preferred_style: str | None = None
    season: str | None = None
    query: str | None = None
    exclude_product_ids: list[str] = Field(default_factory=list)


class RecommendRequest(BaseModel):
    """Recommendation request accepted by /recommend."""

    query: str | None = None
    intent: UserIntent | None = None
    top_k: int = Field(default=30, ge=3, le=100)


class ChatRequest(BaseModel):
    """Conversational request accepted by /chat."""

    message: str = Field(min_length=2)
    profile: UserIntent | None = None


class SimilarItemRequest(BaseModel):
    """Similar item lookup request."""

    item_id: str
    top_k: int = Field(default=8, ge=1, le=50)


class ScoreBreakdownResponse(BaseModel):
    image_similarity: float
    metadata_similarity: float
    category_match: float
    occasion_match: float
    style_match: float
    color_match: float
    season_match: float


class ProductResponse(BaseModel):
    id: str
    name: str
    category_slot: str
    article_type: str
    color: str
    gender: str
    season: str
    usage: str
    image_path: str | None = None
    score: float
    breakdown: ScoreBreakdownResponse


class OutfitResponse(BaseModel):
    topwear: ProductResponse | None
    bottomwear: ProductResponse | None
    footwear: ProductResponse | None
    accessories: list[ProductResponse]
    compatibility_score: float
    reasoning: list[str]
    generated_image_path: str | None = None


class RecommendationResponse(BaseModel):
    intent: UserIntent
    outfits: list[OutfitResponse]
    latency_ms: float
    engine: str = "hybrid-retrieval-ranking"
