"""
Persistence helpers for saving prompts, raw responses, logs, etc.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json
from datetime import datetime


def ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def timestamp_str() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")


def save_text(path: str, content: str) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return str(p)


def save_json(path: str, data: Any) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    return str(p)