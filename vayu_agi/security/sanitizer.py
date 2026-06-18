"""Prompt Sanitization Engine - Prevents basic prompt injection."""
from __future__ import annotations
import re
from ..logger import get_logger

log = get_logger("sanitizer")

class PromptSanitizer:
    INJECTION_PATTERNS = [
        r"ignore (all )?previous instructions",
        r"disregard (all )?prior commands",
        r"you are now (an? )?(evil| unrestricted| jailbroken)",
        r"system prompt:",
    ]

    def sanitize(self, text: str) -> str:
        clean = text
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, clean, re.IGNORECASE):
                log.warning(f"Blocked potential prompt injection: {pattern}")
                clean = re.sub(pattern, "[BLOCKED]", clean, flags=re.IGNORECASE)
        clean = re.sub(r'<script.*?>.*?</script>', '', clean, flags=re.IGNORECASE | re.DOTALL)
        return clean.strip()

SANITIZER = PromptSanitizer()
