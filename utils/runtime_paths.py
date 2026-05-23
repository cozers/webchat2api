from __future__ import annotations

import sys
from pathlib import Path


def source_root() -> Path:
    """Return the project root when running from source."""
    return Path(__file__).resolve().parents[1]


def bundle_root() -> Path:
    """Return PyInstaller's extraction root, or the project root in source mode."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS).resolve()
    return source_root()


def runtime_root() -> Path:
    """Return the writable runtime directory next to the binary in frozen mode."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return source_root()
