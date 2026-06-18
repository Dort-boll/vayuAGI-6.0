"""Global configuration for VAYU AGI 6."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class ModelConfig:
    name: str
    backend: str = "ollama"
    endpoint: str = "http://localhost:11434"
    max_tokens: int = 8192
    temperature: float = 0.7

@dataclass
class VayuConfig:
    data_dir: Path = Path.home() / ".vayu_agi"
    models: dict[str, ModelConfig] = field(default_factory=dict)
    cache_enabled: bool = True
    cache_ttl_sec: int = 86400
    
    # Security Config
    doh_enabled: bool = True
    doh_endpoint: str = "https://1.1.1.1/dns-query"
    rate_limit_per_min: int = 30

    def __post_init__(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._init_models()

    def _init_models(self) -> None:
        self.models = {
            "deepseek-r1": ModelConfig("deepseek-r1", max_tokens=8192, temperature=0.6),
            "nemotron-ultra": ModelConfig("nemotron-ultra", max_tokens=8192, temperature=0.6),
            "deepseek-v3": ModelConfig("deepseek-v3", max_tokens=8192, temperature=0.7),
            "am-thinking": ModelConfig("am-thinking-v1", max_tokens=8192, temperature=0.5),
            "qwen-coder": ModelConfig("qwen2.5-coder", max_tokens=8192, temperature=0.2),
            "qwen3": ModelConfig("qwen2.5", max_tokens=8192, temperature=0.7),
            "llama4-scout": ModelConfig("llama4-scout", max_tokens=1000000, temperature=0.8),
            "phi4": ModelConfig("phi4", max_tokens=4096, temperature=0.7),
        }

    def get(self, key: str) -> ModelConfig:
        if key not in self.models:
            raise KeyError(f"Unknown model key: {key}")
        return self.models[key]

CONFIG = VayuConfig()
