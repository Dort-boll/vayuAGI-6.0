"""Centralized logging with masking for VAYU AGI 6."""
from __future__ import annotations
import logging
import re
from pathlib import Path
from rich.logging import RichHandler

_LOG_DIR = Path.home() / ".vayu_agi" / "logs"
_LOG_DIR.mkdir(parents=True, exist_ok=True)

class MaskingFilter(logging.Filter):
    """Masks sensitive data like API keys in logs."""
    def filter(self, record):
        if isinstance(record.msg, str):
            record.msg = re.sub(r'sk-[a-zA-Z0-9]{20,}', 'sk-****MASKED****', record.msg)
        return True

def get_logger(name: str = "vayu") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers: return logger
    logger.setLevel(logging.DEBUG)
    
    console = RichHandler(rich_tracebacks=True, show_path=False, markup=True)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(console)

    file_handler = logging.FileHandler(_LOG_DIR / "vayu.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s"))
    logger.addHandler(file_handler)
    
    logger.addFilter(MaskingFilter())
    return logger
