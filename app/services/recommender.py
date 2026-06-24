"""Application service composing retrieval, ranking, compatibility, and explanations."""

from __future__ import annotations

import time

import numpy as np

from app.compatibility.engine import CompatibilityEngine
from app.config.settings import get_settings
from app.embeddings.hybrid import build_hybrid_embeddings
from app.embeddings.image import load_or_create_image_embeddings
from app.embeddings.text import MetadataEmbedder, load_or_create_metadata_embeddings
from app.models.product import Outfit, Product, RankedProduct
from app.ranking.ranker import HybridRanker
from app.retrieval.faiss_store import VectorStore
from app.schemas.recommendation import RecommendationResponse, UserIntent
from app.services.image_composer import OutfitImageComposer
from app.services.catalog import load_catalog
from app.utils.serialization import outfit_to_response


class RecommendationService:
    """High-level recommendation orchestration."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.products = load_catalog(
            self.settings.data_path,
            self.settings.sample_data_path,
            self.settings.darex_dataset_dir,
        )
        self.product_by_id = {product.id: product for product in self.products}
        self.text_embedder = MetadataEmbedder()
        descriptions = [product.semantic_description for product in self.products]
        self.metadata_vectors = load_or_create_metadata_embeddings(
            descriptions, self.settings.cache_dir / "metadata_embeddings.joblib", self.text_embedder
        )
        self.image_vectors = load_or_create_image_embeddings(
            [product.image_path for product in self.products],
            self.metadata_vectors,
            self.settings.cache_dir / "image_embeddings.joblib",
        )
        self.hybrid_vectors = build_hybrid_embeddings(
            self.image_vectors,
            self.metadata_vectors,
            self.settings.image_weight,
            self.settings.metadata_weight,
        )
        self.vector_store = VectorStore(self.hybrid_vectors, [product.id for product in self.products])
        self.compatibility = CompatibilityEngine()
        self.ranker = HybridRanker(self.compatibility)
        self.image_composer = OutfitImageComposer(self.settings.cache_dir / "generated_outfits")

    def recommend(self, intent: UserIntent, top_k: int | None = None) -> RecommendationResponse:
        """Return complete outfit recommendations for structured intent."""

        started = time.perf_counter()
        intent = self._normalize_intent(intent)
        candidates = self._retrieve(intent, top_k or self.settings.top_k)
        outfits = self._assemble_outfits(candidates, intent)
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        return RecommendationResponse(
            intent=intent,
            outfits=[outfit_to_response(outfit) for outfit in outfits],
            latency_ms=latency_ms,
        )

    def similar_items(self, item_id: str, top_k: int = 8) -> list[Product]:
        """Find similar catalog items by hybrid vector."""

        if item_id not in self.product_by_id:
            raise KeyError(f"Unknown item_id: {item_id}")
        index = [product.id for product in self.products].index(item_id)
        results = self.vector_store.search(self.hybrid_vectors[index], top_k + 1)
        return [self.product_by_id[result_id] for result_id, _ in results if result_id != item_id][:top_k]

    def _retrieve(self, intent: UserIntent, top_k: int) -> list[tuple[Product, float, float]]:
        top_k = min(len(self.products), max(top_k, len(self.products)))
        query_text = self._intent_to_query(intent)
        metadata_query = self.text_embedder.encode([query_text])
        image_width = self.image_vectors.shape[1]
        image_query = np.zeros((1, image_width), dtype=np.float32)
        width = min(image_width, metadata_query.shape[1])
        image_query[:, :width] = metadata_query[:, :width]
        hybrid_query = build_hybrid_embeddings(
            image_query,
            metadata_query,
            self.settings.image_weight,
            self.settings.metadata_weight,
        )[0]
        results = self.vector_store.search(hybrid_query, top_k)
        candidates: list[tuple[Product, float, float]] = []
        excluded = set(intent.exclude_product_ids)
        for product_id, hybrid_score in results:
            if product_id in excluded:
                continue
            product = self.product_by_id[product_id]
            idx = [item.id for item in self.products].index(product_id)
            metadata_score = float(self.metadata_vectors[idx] @ metadata_query[0])
            candidates.append((product, float(hybrid_score), metadata_score))
        return candidates

    def _normalize_intent(self, intent: UserIntent) -> UserIntent:
        """Make profile-only/generic prompts map to dataset-relevant intent."""

        updates = {}
        if intent.preferred_style == "ethnic" and intent.occasion in {"casual", "", None}:
            updates["occasion"] = "festive"
        if intent.season == "winter" and intent.occasion in {"casual", "", None} and not intent.preferred_style:
            updates["occasion"] = "winter"
        if updates:
            return intent.model_copy(update=updates)
        return intent

    def _assemble_outfits(self, candidates: list[tuple[Product, float, float]], intent: UserIntent) -> list[Outfit]:
        ranked_by_slot: dict[str, list[RankedProduct]] = {}
        for slot in ("topwear", "bottomwear", "footwear", "accessory"):
            ranked_by_slot[slot] = self.ranker.rank(candidates, intent, slot)
            ranked_by_slot[slot] = [item for item in ranked_by_slot[slot] if item.product.category_slot == slot]
            occasion_matched = [
                item for item in ranked_by_slot[slot] if self.compatibility.occasion_match(item.product, intent.occasion) >= 0.8
            ]
            if occasion_matched:
                ranked_by_slot[slot] = occasion_matched
            elif intent.occasion not in {"casual", "", None}:
                ranked_by_slot[slot] = []
            ranked_by_slot[slot] = ranked_by_slot[slot][:5]

        outfits: list[Outfit] = []
        if not ranked_by_slot["topwear"]:
            footwear = ranked_by_slot["footwear"][0] if ranked_by_slot["footwear"] else None
            accessories = ranked_by_slot["accessory"][:2]
            outfit = Outfit(
                topwear=None,
                bottomwear=None,
                footwear=footwear,
                accessories=accessories,
                compatibility_score=0.0,
                reasoning=[
                    "The dataset does not contain a valid-image topwear item for this gender, style, and occasion.",
                    "Showing the valid matching dataset pieces that are available instead of hallucinating missing products.",
                ],
            )
            outfit.generated_image_path = self.image_composer.compose(outfit, 0)
            return [outfit]

        for top in ranked_by_slot["topwear"][:3]:
            bottom = None if top.product.is_one_piece else self._best_pair(top, ranked_by_slot["bottomwear"])
            footwear = self._best_pair(top, ranked_by_slot["footwear"], intent)
            accessories = self._suitable_accessories(ranked_by_slot["accessory"], intent)
            score = self.compatibility.outfit_score(
                top.product,
                bottom.product if bottom else None,
                footwear.product if footwear else None,
            )
            reasoning = self.compatibility.explain(
                top.product,
                bottom.product if bottom else None,
                footwear.product if footwear else None,
            )
            if footwear is None:
                reasoning.append(
                    "No footwear was added because the dataset does not contain a valid-image footwear item matching this gender and occasion."
                )
            outfits.append(Outfit(top, bottom, footwear, accessories, score, reasoning))
        sorted_outfits = sorted(outfits, key=lambda outfit: outfit.compatibility_score, reverse=True)[:3]
        for index, outfit in enumerate(sorted_outfits):
            outfit.generated_image_path = self.image_composer.compose(outfit, index)
        return sorted_outfits

    def _best_pair(
        self,
        anchor: RankedProduct,
        options: list[RankedProduct],
        intent: UserIntent | None = None,
    ) -> RankedProduct | None:
        if not options:
            return None
        if intent is not None:
            suitable = [item for item in options if self.compatibility.occasion_match(item.product, intent.occasion) >= 0.8]
            if not suitable:
                return None
            options = suitable
        return max(
            options,
            key=lambda option: option.score + self.compatibility.pair_score(anchor.product, option.product) * 20,
        )

    def _suitable_accessories(self, options: list[RankedProduct], intent: UserIntent) -> list[RankedProduct]:
        suitable = [item for item in options if self.compatibility.occasion_match(item.product, intent.occasion) >= 0.8]
        return suitable[:1]

    def _intent_to_query(self, intent: UserIntent) -> str:
        return " ".join(
            part
            for part in [
                intent.query,
                intent.occasion,
                intent.gender,
                intent.preferred_style,
                intent.season,
                " ".join(intent.preferred_colors),
            ]
            if part
        )
