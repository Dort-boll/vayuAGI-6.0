"""Self-Reflection Engine — model critiques and refines its own answer."""
from __future__ import annotations
from ..llm.backend import get_backend
from ..logger import get_logger

log = get_logger("reflection")

class SelfReflection:
    def __init__(self, model_key: str = "deepseek-r1") -> None:
        self.model = get_backend(model_key)

    def refine(self, question: str, answer: str) -> str:
        prompt = (
            f"Question: {question}\n"
            f"Proposed Answer: {answer}\n"
            "Critique the proposed answer for accuracy and hallucinations. "
            "If correct, return the original answer. If flawed, provide the corrected and improved final answer."
        )
        try:
            return self.model.generate(prompt, temperature=0.2)
        except Exception as exc:
            log.warning(f"Self-reflection failed: {exc}")
            return answer
