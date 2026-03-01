"""LLM-gränssnitt med lokal modell + extern API fallback."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Protocol


class LLMClient(Protocol):
    def generate(self, prompt: str) -> str:
        ...


@dataclass
class LocalRuleBasedLLM:
    """Offline fallback that emits a robust multi-tool plan JSON."""

    model_name: str = "local-rule-7b-sim"

    def generate(self, prompt: str) -> str:
        goal = prompt.split("GOAL:", 1)[-1].strip() or "okänt mål"
        plan = {
            "goal": goal,
            "steps": [
                {"id": 1, "type": "decompose", "action": "Analysera mål och delmål", "tool": "python"},
                {"id": 2, "type": "orchestrate", "action": "Starta SuperAGI workflow", "tool": "superagi"},
                {"id": 3, "type": "act_gui", "action": "Ta screenshot via Agent-S", "tool": "agent_s"},
                {"id": 4, "type": "verify", "action": "Verifiera artefakter lokalt", "tool": "shell"},
            ],
        }
        return json.dumps(plan, ensure_ascii=False)


@dataclass
class ExternalAPILLM:
    endpoint: str
    api_key: str
    model_name: str

    def generate(self, prompt: str) -> str:
        import requests

        response = requests.post(
            self.endpoint,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model_name, "prompt": prompt, "temperature": 0.1},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("text", "")


def build_llm_client() -> LLMClient:
    endpoint = os.getenv("ARVIVA_LLM_ENDPOINT")
    api_key = os.getenv("ARVIVA_LLM_API_KEY")
    model = os.getenv("ARVIVA_LLM_MODEL", "local-rule-7b-sim")
    if endpoint and api_key:
        return ExternalAPILLM(endpoint=endpoint, api_key=api_key, model_name=model)
    return LocalRuleBasedLLM(model_name=model)
