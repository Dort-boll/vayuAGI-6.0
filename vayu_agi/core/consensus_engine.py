"""Advanced Consensus Engine — uses a master model to synthesize multi-model answers."""
from __future__ import annotations
from typing import Any
from ..llm.backend import get_backend
from ..logger import get_logger

log = get_logger("consensus")

class ConsensusEngine:
    def __init__(self) -> None:
        self.models = ["qwen3", "deepseek-v3", "llama4-scout"]
        self.synthesizer = get_backend("deepseek-r1")

    def vote(self, prompt: str, system: str | None = None) -> dict[str, Any]:
        responses = {}
        for key in self.models:
            try:
                responses[key] = get_backend(key).generate(prompt, system=system)
            except Exception as exc:
                log.warning(f"Model {key} failed in consensus: {exc}")

        if not responses:
            return {"answer": "[Consensus failed] No models responded.", "sources": []}

        synth_prompt = "You are the VAYU AGI Master Synthesizer. Review the following answers from different AI models. Synthesize the absolute best, most accurate, and complete unified answer.\n\n"
        for model, ans in responses.items():
            synth_prompt += f"--- {model} ---\n{ans}\n\n"
        synth_prompt += "--- FINAL SYNTHESIS ---\n"

        try:
            final_answer = self.synthesizer.generate(synth_prompt, temperature=0.3)
        except Exception:
            final_answer = list(responses.values())[0]

        return {"answer": final_answer, "sources": list(responses.keys())}
