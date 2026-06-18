"""Audio Engine — Text-to-Speech (TTS) and Speech-to-Text (STT)."""
from __future__ import annotations
import threading
from ..logger import get_logger

log = get_logger("audio")

class AudioEngine:
    def __init__(self):
        self.engine = None
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 170)
        except Exception as e:
            log.warning(f"TTS engine initialization failed: {e}")

    def speak(self, text: str) -> None:
        if not self.engine:
            log.warning("TTS unavailable.")
            return
        def _run():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                log.error(f"TTS error: {e}")
        threading.Thread(target=_run, daemon=True).start()
