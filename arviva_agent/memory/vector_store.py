"""En enkel in-memory vektorstore för semantisk återhämtning."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass
class VectorItem:
    key: str
    vector: list[float]
    payload: dict


class VectorStore:
    def __init__(self) -> None:
        self._items: list[VectorItem] = []

    def upsert(self, item: VectorItem) -> None:
        self._items = [i for i in self._items if i.key != item.key]
        self._items.append(item)

    def _cosine(self, a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sqrt(sum(x * x for x in a)) or 1.0
        norm_b = sqrt(sum(y * y for y in b)) or 1.0
        return dot / (norm_a * norm_b)

    def query(self, vector: list[float], top_k: int = 3) -> list[VectorItem]:
        scored = sorted(self._items, key=lambda it: self._cosine(it.vector, vector), reverse=True)
        return scored[:top_k]
