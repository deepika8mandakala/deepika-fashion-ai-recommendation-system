"""Warm embedding caches and vector index."""

from app.services.recommender import RecommendationService


if __name__ == "__main__":
    service = RecommendationService()
    service.vector_store.save(service.settings.vector_store_dir / "hybrid_index.joblib")
    print(f"Indexed {len(service.products)} products.")

