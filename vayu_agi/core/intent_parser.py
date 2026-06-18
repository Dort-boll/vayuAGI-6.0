"""True AGI Intent Parser — determines what tools the AGI needs."""
from __future__ import annotations
from enum import Enum

class Intent(str, Enum):
    TEXT = "text"
    WEB_SEARCH = "web_search"
    IMAGE_GEN = "image_gen"
    VIDEO_GEN = "video_gen"
    TTS = "tts"

class IntentParser:
    @staticmethod
    def parse(query: str) -> Intent:
        q = query.lower().strip()
        if any(kw in q for kw in ["search", "google", "look up", "latest news", "find online"]):
            return Intent.WEB_SEARCH
        if any(kw in q for kw in ["generate image", "draw", "create image", "picture of", "render of"]):
            return Intent.IMAGE_GEN
        if any(kw in q for kw in ["generate video", "animate", "create video", "video of"]):
            return Intent.VIDEO_GEN
        if any(kw in q for kw in ["speak", "read aloud", "say this", "tts"]):
            return Intent.TTS
        return Intent.TEXT
