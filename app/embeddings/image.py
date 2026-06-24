"""Image embedding providers with optional FashionCLIP/CLIP support."""

from __future__ import annotations

from pathlib import Path
import pickle

import numpy as np


class ImageEmbedder:
    """Generate image embeddings, falling back to metadata-like deterministic vectors."""

    def __init__(self, dim: int = 512) -> None:
        self.dim = dim
        self._fashion_clip = None
        try:
            from fashion_clip.fashion_clip import FashionCLIP

            self._fashion_clip = FashionCLIP("fashion-clip")
        except Exception:
            self._fashion_clip = None

    def encode(self, image_paths: list[str | None], fallback_text_vectors: np.ndarray) -> np.ndarray:
        """Return L2-normalized image vectors with incremental-safe fallback."""

        if self._fashion_clip is not None and any(image_paths):
            valid_paths = [path for path in image_paths if path and Path(path).exists()]
            if len(valid_paths) == len(image_paths):
                vectors = self._fashion_clip.encode_images(valid_paths, batch_size=32)
                return _normalize(np.asarray(vectors, dtype=np.float32))

        if fallback_text_vectors.shape[1] == self.dim:
            return _normalize(fallback_text_vectors.astype(np.float32))
        projected = np.zeros((fallback_text_vectors.shape[0], self.dim), dtype=np.float32)
        width = min(self.dim, fallback_text_vectors.shape[1])
        projected[:, :width] = fallback_text_vectors[:, :width]
        return _normalize(projected)


def _normalize(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vectors / norms


def load_or_create_image_embeddings(
    image_paths: list[str | None],
    fallback_text_vectors: np.ndarray,
    cache_path: Path,
    embedder: ImageEmbedder | None = None,
) -> np.ndarray:
    """Cache image embeddings; missing images use deterministic fallback vectors."""

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    if cache_path.exists():
        with cache_path.open("rb") as file:
            cached = pickle.load(file)
        if getattr(cached, "shape", (0,))[0] == len(image_paths):
            return cached
    vectors = (embedder or ImageEmbedder()).encode(image_paths, fallback_text_vectors)
    with cache_path.open("wb") as file:
        pickle.dump(vectors, file)
    return vectors
