"""Launch VAYU AGI 6 GUI."""
from __future__ import annotations
import sys
from vayu_agi.gui.app import VayuAGIApp
from vayu_agi.logger import get_logger

log = get_logger("main")

def main() -> int:
    try:
        log.info("Starting VAYU AGI 6…")
        app = VayuAGIApp()
        app.mainloop()
        return 0
    except KeyboardInterrupt:
        return 0
    except Exception as exc:
        log.exception(f"Fatal: {exc}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
