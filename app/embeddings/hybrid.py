"""Hybrid embedding construction."""

from __future__ import annotations

from pathlib import Path
import pickle

import numpy as np


def normalize(vectors: np.ndarray) -> np.ndarray:
    """L2-normalize row vectors."""

    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vectors / norms


def build_hybrid_embeddings(
    image_vectors: np.ndarray,
    metadata_vectors: np.ndarray,
    image_weight: float = 0.55,
    metadata_weight: float = 0.45,
) -> np.ndarray:
    """Weighted concatenation captures visual and semantic item similarity."""

    image_part = normalize(image_vectors) * image_weight
    metadata_part = normalize(metadata_vectors) * metadata_weight
    return normalize(np.concatenate([image_part, metadata_part], axis=1).astype(np.float32))


def load_or_create_hybrid_embeddings(
    image_vectors: np.ndarray,
    metadata_vectors: np.ndarray,
    cache_path: Path,
    image_weight: float = 0.55,
    metadata_weight: float = 0.45,
) -> np.ndarray:
    """Persist hybrid embeddings for low-latency startup."""

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    if cache_path.exists():
        with cache_path.open("rb") as file:
            return pickle.load(file)
    vectors = build_hybrid_embeddings(image_vectors, metadata_vectors, image_weight, metadata_weight)
    with cache_path.open("wb") as file:
        pickle.dump(vectors, file)
    return vectors
