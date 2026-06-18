"""Orchestrator — the heart of VAYU AGI 6."""
from __future__ import annotations
import time
from typing import Any
from ..llm.backend import get_backend
from ..logger import get_logger
from ..memory.memory_fabric import MemoryFabric
from ..multimodal.web_search import WebSearch
from ..multimodal.media_gen import MediaGenerator
from ..multimodal.audio import AudioEngine
from ..reasoning.self_reflection import SelfReflection
from ..security.sanitizer import SANITIZER
from ..security.rate_limiter import RATE_LIMITER
from ..exceptions import RateLimitError
from .cognitive_router import CognitiveRouter
from .consensus_engine import ConsensusEngine
from .intent_parser import IntentParser, Intent

log = get_logger("orchestrator")

class Orchestrator:
    def __init__(self) -> None:
        self.router = CognitiveRouter()
        self.consensus = ConsensusEngine()
        self.memory = MemoryFabric()
        self.intent_parser = IntentParser()
        self.web_search = WebSearch()
        self.media_gen = MediaGenerator()
        self.audio = AudioEngine()
        self.reflection = SelfReflection()

    def run(self, query: str) -> dict[str, Any]:
        start = time.time()
        try:
            RATE_LIMITER.check()
            clean_query = SANITIZER.sanitize(query)
            
            cached = self.memory.lookup(clean_query)
            if cached:
                return {"answer": cached["answer"], "source": "semantic_cache", "elapsed": 0.0, "model": "memory", "plan": {"complexity": "trivial", "domain": "cache", "intent": "text"}, "media": None}

            intent = self.intent_parser.parse(clean_query)
            
            if intent == Intent.WEB_SEARCH:
                answer = self.web_search.search(clean_query)
                model_used = "DuckDuckGo (DoH)"
                plan = {"complexity": "simple", "domain": "web", "intent": intent.value}
                media = None
            elif intent == Intent.IMAGE_GEN:
                img_url = self.media_gen.generate_image(clean_query)
                answer = "Image generated successfully."
                model_used = "Pollinations AI (DoH)"
                plan = {"complexity": "medium", "domain": "image", "intent": intent.value}
                media = {"type": "image", "url": img_url}
            elif intent == Intent.VIDEO_GEN:
                answer = self.media_gen.generate_video(clean_query)
                model_used = "Video API"
                plan = {"complexity": "complex", "domain": "video", "intent": intent.value}
                media = None
            elif intent == Intent.TTS:
                text_to_speak = clean_query.replace("read aloud", "").replace("speak", "").strip()
                self.audio.speak(text_to_speak)
                answer = f"Spoken aloud: {text_to_speak}"
                model_used = "pyttsx3"
                plan = {"complexity": "simple", "domain": "audio", "intent": intent.value}
                media = None
            else:
                decision = self.router.route(clean_query)
                plan = {
                    "query": clean_query,
                    "complexity": decision.complexity.value,
                    "domain": decision.domain,
                    "intent": intent.value,
                    "primary_model": decision.primary_model,
                    "model_chain": decision.model_chain,
                    "use_consensus": decision.complexity.value in {"complex", "frontier"},
                    "use_reflection": decision.complexity.value in {"medium", "complex", "frontier"},
                }
                answer, model_used = self._execute_text(plan, clean_query)
                media = None

            self.memory.store(clean_query, answer, metadata=plan)
            return {"answer": answer, "source": "live", "model": model_used, "plan": plan, "elapsed": round(time.time() - start, 3), "media": media}
            
        except RateLimitError as exc:
            log.warning(f"Rate limited: {exc}")
            return {"answer": "[Security Block] You are sending requests too fast.", "source": "error", "elapsed": 0.0, "plan": {}, "media": None}
        except Exception as exc:
            log.exception(f"Orchestration failed: {exc}")
            return {"answer": f"[VAYU error] {exc}", "source": "error", "elapsed": 0.0, "plan": {}, "media": None}

    def _execute_text(self, plan: dict, query: str) -> tuple[str, str]:
        if plan.get("use_consensus"):
            result = self.consensus.vote(query)
            answer = result["answer"]
            model_used = "Consensus(Synthesized)"
        else:
            answer = ""
            model_used = "none"
            for model_key in plan["model_chain"]:
                try:
                    backend = get_backend(model_key)
                    ans = backend.generate(query)
                    if "offline" not in ans.lower():
                        answer = ans
                        model_used = model_key
                        break
                except Exception:
                    continue

        # Self-Reflection for Accuracy
        if plan.get("use_reflection") and answer and "error" not in answer.lower():
            try:
                answer = self.reflection.refine(query, answer)
                model_used += " + Reflection"
            except Exception as exc:
                log.warning(f"Self-reflection failed: {exc}")

        return answer, model_used
