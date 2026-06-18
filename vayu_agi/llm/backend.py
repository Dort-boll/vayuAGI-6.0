"""Unified LLM backend with graceful offline fallback."""
from __future__ import annotations
import time
import hashlib
import random
import requests
from ..config import CONFIG, ModelConfig
from ..exceptions import ModelUnavailableError
from ..logger import get_logger

log = get_logger("llm")

class LLMBackend:
    def __init__(self, model_cfg: ModelConfig) -> None:
        self.cfg = model_cfg
        self._session = requests.Session()

    def generate(self, prompt: str, *, system: str | None = None, temperature: float | None = None, max_tokens: int | None = None) -> str:
        try:
            if self.cfg.backend == "ollama":
                return self._call_ollama(prompt, system, temperature, max_tokens)
        except Exception as exc:
            log.warning(f"Backend '{self.cfg.name}' failed: {exc}. Using offline stub.")
        return self._offline_stub(prompt)

    def _call_ollama(self, prompt: str, system: str | None, temp: float | None, mt: int | None) -> str:
        url = f"{self.cfg.endpoint}/api/generate"
        payload = {
            "model": self.cfg.name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temp if temp is not None else self.cfg.temperature,
                "num_predict": mt if mt is not None else self.cfg.max_tokens,
            },
        }
        if system: payload["system"] = system
        resp = self._session.post(url, json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json().get("response", "").strip()

    def _offline_stub(self, prompt: str) -> str:
        h = hashlib.sha256(prompt.encode()).hexdigest()[:8]
        random.seed(int(h, 16))
        replies = [
            f"[{self.cfg.name} offline] Processed securely (hash {h}). Connect Ollama for live reasoning.",
            f"[{self.cfg.name} offline] Cognitive router selected this model. Inference unavailable.",
        ]
        time.sleep(0.05)
        return random.choice(replies)

_REGISTRY: dict[str, LLMBackend] = {}

def get_backend(model_key: str) -> LLMBackend:
    if model_key not in _REGISTRY:
        if model_key not in CONFIG.models:
            raise ModelUnavailableError(f"Unknown model: {model_key}")
        _REGISTRY[model_key] = LLMBackend(CONFIG.models[model_key])
    return _REGISTRY[model_key]
