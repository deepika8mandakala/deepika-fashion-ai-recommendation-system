"""FAISS-backed nearest-neighbor search with numpy fallback."""

from __future__ import annotations

from pathlib import Path
import pickle

import numpy as np


class VectorStore:
    """Vector index abstraction so ranking code is independent from FAISS."""

    def __init__(self, vectors: np.ndarray, ids: list[str]) -> None:
        self.vectors = vectors.astype(np.float32)
        self.ids = ids
        self._faiss_index = None
        try:
            import faiss

            self._faiss = faiss
            self._faiss_index = faiss.IndexFlatIP(self.vectors.shape[1])
            self._faiss_index.add(self.vectors)
        except Exception:
            self._faiss = None

    def search(self, query_vector: np.ndarray, top_k: int) -> list[tuple[str, float]]:
        """Return item ids and cosine/IP scores."""

        query = query_vector.astype(np.float32).reshape(1, -1)
        if self._faiss_index is not None:
            scores, indices = self._faiss_index.search(query, top_k)
            return [(self.ids[int(index)], float(score)) for index, score in zip(indices[0], scores[0]) if index >= 0]

        scores = self.vectors @ query.reshape(-1)
        order = np.argsort(scores)[::-1][:top_k]
        return [(self.ids[int(index)], float(scores[index])) for index in order]

    def save(self, path: Path) -> None:
        """Persist fallback-compatible vectors and ids."""

        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as file:
            pickle.dump({"vectors": self.vectors, "ids": self.ids}, file)

    @classmethod
    def load(cls, path: Path) -> "VectorStore":
        """Load a persisted vector store."""

        with path.open("rb") as file:
            payload = pickle.load(file)
        return cls(payload["vectors"], payload["ids"])
