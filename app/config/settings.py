"""Application settings loaded from environment variables."""

from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def project_path(value: str) -> Path:
    """Resolve relative paths from the repository root."""

    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


@dataclass(frozen=True)
class Settings:
    """Runtime configuration for API, model paths, and scoring."""

    app_name: str = "Fashion AI Outfit Recommender"
    environment: str = "development"
    gemini_api_key: str | None = None
    data_path: Path = Path("data/processed/products_clean.csv")
    sample_data_path: Path = Path("data/sample_products.csv")
    darex_dataset_dir: Path = Path("data/darex")
    vector_store_dir: Path = Path("vector_store")
    cache_dir: Path = Path("cache")
    top_k: int = 30
    image_weight: float = 0.55
    metadata_weight: float = 0.45
    use_transformer_embeddings: bool = False


@lru_cache
def get_settings() -> Settings:
    """Return cached process-wide settings."""

    return Settings(
        app_name=os.getenv("APP_NAME", "Fashion AI Outfit Recommender"),
        environment=os.getenv("ENVIRONMENT", "development"),
        gemini_api_key=os.getenv("GEMINI_API_KEY") or None,
        data_path=project_path(os.getenv("DATA_PATH", "data/processed/products_clean.csv")),
        sample_data_path=project_path(os.getenv("SAMPLE_DATA_PATH", "data/sample_products.csv")),
        darex_dataset_dir=project_path(os.getenv("DAREX_DATASET_DIR", "data/darex")),
        vector_store_dir=project_path(os.getenv("VECTOR_STORE_DIR", "vector_store")),
        cache_dir=project_path(os.getenv("CACHE_DIR", "cache")),
        top_k=int(os.getenv("TOP_K", "30")),
        image_weight=float(os.getenv("IMAGE_WEIGHT", "0.55")),
        metadata_weight=float(os.getenv("METADATA_WEIGHT", "0.45")),
        use_transformer_embeddings=os.getenv("USE_TRANSFORMER_EMBEDDINGS", "false").lower() == "true",
    )
