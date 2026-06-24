"""FastAPI entry point for the Fashion AI recommendation service."""

from functools import lru_cache

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from app.config.settings import get_settings
from app.llm.gemini import GeminiIntentParser
from app.logging.logger import configure_logging
from app.schemas.recommendation import (
    ChatRequest,
    RecommendRequest,
    RecommendationResponse,
    SimilarItemRequest,
    UserIntent,
)
from app.services.recommender import RecommendationService


# --------------------------------------------------
# App Initialization
# --------------------------------------------------

configure_logging()
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
)

from pathlib import Path

# --------------------------------------------------
# Static File Configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

IMAGES_DIR = BASE_DIR / "data" / "darex" / "images"
GENERATED_DIR = BASE_DIR / "cache" / "generated_outfits"

print("IMAGES_DIR =", IMAGES_DIR)
print("GENERATED_DIR =", GENERATED_DIR)

app.mount(
    "/images",
    StaticFiles(directory=str(IMAGES_DIR)),
    name="images",
)

app.mount(
    "/generated",
    StaticFiles(directory=str(GENERATED_DIR)),
    name="generated",
)
@lru_cache
def get_recommender() -> RecommendationService:
    return RecommendationService()


@lru_cache
def get_intent_parser() -> GeminiIntentParser:
    return GeminiIntentParser()


# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------

@app.get("/")
def root() -> dict[str, object]:
    return {
        "app": settings.app_name,
        "status": "ok",
        "docs": "/docs",
        "health": "/health",
        "chat": {
            "method": "POST",
            "path": "/chat",
        },
        "recommend": {
            "method": "POST",
            "path": "/recommend",
        },
    }


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "engine": "hybrid-retrieval-ranking",
    }


# --------------------------------------------------
# Recommendation Endpoint
# --------------------------------------------------

@app.post(
    "/recommend",
    response_model=RecommendationResponse,
)
def recommend(
    request: RecommendRequest,
) -> RecommendationResponse:

    if request.intent is None and not request.query:
        raise HTTPException(
            status_code=422,
            detail="Provide either query or structured intent.",
        )

    intent = request.intent or get_intent_parser().parse(
        request.query or ""
    )

    if request.query and intent.query is None:
        intent.query = request.query

    return get_recommender().recommend(
        intent,
        request.top_k,
    )


# --------------------------------------------------
# Conversational Endpoint
# --------------------------------------------------

@app.post(
    "/chat",
    response_model=RecommendationResponse,
)
def chat(
    request: ChatRequest,
) -> RecommendationResponse:

    intent = get_intent_parser().parse(
        request.message,
        request.profile,
    )

    return get_recommender().recommend(intent)


# --------------------------------------------------
# Profile Endpoint
# --------------------------------------------------

@app.post("/profile")
def profile(
    intent: UserIntent,
) -> dict[str, object]:

    return {
        "status": "accepted",
        "profile": intent.model_dump(),
    }


# --------------------------------------------------
# Similar Item Endpoint
# --------------------------------------------------

@app.post("/similar-item")
def similar_item(
    request: SimilarItemRequest,
) -> dict[str, object]:

    try:
        products = get_recommender().similar_items(
            request.item_id,
            request.top_k,
        )

    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return {
        "item_id": request.item_id,
        "results": [
            {
                "id": product.id,
                "name": product.product_display_name,
                "article_type": product.article_type,
                "color": product.base_colour,
                "usage": product.usage,
            }
            for product in products
        ],
    }


# --------------------------------------------------
# Metrics Endpoint
# --------------------------------------------------

@app.get("/metrics")
def metrics() -> dict[str, object]:

    recommender = get_recommender()

    return {
        "catalog_size": len(recommender.products),
        "vector_dimension": int(
            recommender.hybrid_vectors.shape[1]
        ),
        "index": (
            "faiss"
            if recommender.vector_store._faiss_index is not None
            else "numpy"
        ),
    }
