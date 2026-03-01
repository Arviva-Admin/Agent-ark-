"""Persistens av agenthistorik till JSONL + enkel semantisk indexering."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from arviva_agent.memory.vector_store import VectorItem, VectorStore


@dataclass
class MemoryStore:
    path: Path = Path("data/agent_history.jsonl")
    events: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.vector_store = VectorStore()

    def append(self, event_type: str, payload: dict[str, Any]) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "payload": payload,
        }
        self.events.append(entry)
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def recent_events(self, limit: int = 10) -> list[dict[str, Any]]:
        return self.events[-limit:]

    def embed_and_store(self, key: str, text: str, payload: dict[str, Any]) -> None:
        vec = [0.0] * 8
        for char in text.lower():
            vec[ord(char) % 8] += 1.0
        norm = sum(vec) or 1.0
        vec = [value / norm for value in vec]
        self.vector_store.upsert(VectorItem(key=key, vector=vec, payload=payload))

    def recall(self, text: str) -> list[dict[str, Any]]:
        vec = [0.0] * 8
        for char in text.lower():
            vec[ord(char) % 8] += 1.0
        norm = sum(vec) or 1.0
        vec = [value / norm for value in vec]
        return [item.payload for item in self.vector_store.query(vec)]
