"""Cognitive Router — routes tasks to the cheapest capable model first."""
from __future__ import annotations
import re
from dataclasses import dataclass
from enum import Enum
from ..logger import get_logger

log = get_logger("router")

class Complexity(str, Enum):
    TRIVIAL = "trivial"
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    FRONTIER = "frontier"

_MODEL_LADDER: dict[str, list[str]] = {
    "default": ["phi4", "qwen3", "deepseek-v3", "deepseek-r1", "nemotron-ultra"],
    "coding":  ["phi4", "qwen-coder", "deepseek-r1"],
    "logic":   ["phi4", "am-thinking", "deepseek-r1", "nemotron-ultra"],
    "research":["phi4", "qwen3", "deepseek-v3", "deepseek-r1"],
    "creative":["phi4", "llama4-scout", "qwen3"],
}

@dataclass
class RouteDecision:
    complexity: Complexity
    domain: str
    model_chain: list[str]
    primary_model: str

class CognitiveRouter:
    def route(self, query: str) -> RouteDecision:
        q = query.lower().strip()
        complexity = self._estimate_complexity(q)
        domain = self._estimate_domain(q)
        chain = _MODEL_LADDER.get(domain, _MODEL_LADDER["default"])
        idx = min({"trivial": 0, "simple": 0, "medium": 1, "complex": 2, "frontier": 4}[complexity.value], len(chain) - 1)
        return RouteDecision(complexity, domain, chain, chain[idx])

    @staticmethod
    def _estimate_complexity(q: str) -> Complexity:
        if any(kw in q for kw in ["hi", "hello", "thanks"]): return Complexity.TRIVIAL
        if any(kw in q for kw in ["what is", "define", "summarize"]): return Complexity.SIMPLE
        if any(kw in q for kw in ["explain", "compare", "analyze"]): return Complexity.MEDIUM
        if any(kw in q for kw in ["prove", "derive", "design", "build"]): return Complexity.COMPLEX
        if any(kw in q for kw in ["novel", "discover", "hypothesis"]): return Complexity.FRONTIER
        return Complexity.MEDIUM

    @staticmethod
    def _estimate_domain(q: str) -> str:
        if re.search(r"\b(code|python|function|bug|api|debug)\b", q): return "coding"
        if re.search(r"\b(math|prove|theorem|equation|physics)\b", q): return "logic"
        if re.search(r"\b(research|paper|study|literature)\b", q): return "research"
        if re.search(r"\b(poem|story|write|creative|essay)\b", q): return "creative"
        return "default"
