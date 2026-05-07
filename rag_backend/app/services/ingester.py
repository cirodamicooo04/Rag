from pathlib import Path
from typing import Optional


def safe_text(s: Optional[str]) -> str:
    return (s or "").strip()

def process_document(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    text = path.read_text(encoding="utf-8", errors="ignore")

    return safe_text(text)