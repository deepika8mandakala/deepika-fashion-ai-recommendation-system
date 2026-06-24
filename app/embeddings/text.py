"""Metadata embedding providers with deterministic fallback."""

from __future__ import annotations

import hashlib
from pathlib import Path
import pickle
import re

import numpy as np

from app.config.settings import get_settings


class MetadataEmbedder:
    """Encode semantic descriptions using sentence-transformers or hashing fallback."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", dim: int = 384) -> None:
        self.model_name = model_name
        self.dim = dim
        self._model = None
        if not get_settings().use_transformer_embeddings:
            return
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(model_name)
        except Exception:
            self._model = None

    def encode(self, texts: list[str]) -> np.ndarray:
        """Return L2-normalized text embeddings."""

        if self._model is not None:
            vectors = self._model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
            return np.asarray(vectors, dtype=np.float32)
        vectors = np.zeros((len(texts), self.dim), dtype=np.float32)
        for row, text in enumerate(texts):
            tokens = re.findall(r"[a-z0-9]+", text.lower())
            for token in tokens:
                digest = hashlib.md5(token.encode("utf-8")).hexdigest()
                vectors[row, int(digest, 16) % self.dim] += 1.0
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return vectors / norms


def load_or_create_metadata_embeddings(
    texts: list[str],
    cache_path: Path,
    embedder: MetadataEmbedder | None = None,
) -> np.ndarray:
    """Cache embeddings to avoid repeated model inference."""

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    if cache_path.exists():
        with cache_path.open("rb") as file:
            cached = pickle.load(file)
        if getattr(cached, "shape", (0,))[0] == len(texts):
            return cached
    vectors = (embedder or MetadataEmbedder()).encode(texts)
    with cache_path.open("wb") as file:
        pickle.dump(vectors, file)
    return vectors
