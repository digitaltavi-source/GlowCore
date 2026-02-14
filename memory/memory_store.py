from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List

class MemoryStore:
    def __init__(self, path: str = "glow_memory.json"):
        self.path = Path(path)

    def append(self, item: Dict[str, Any]) -> None:
        data: List[Dict[str, Any]] = []
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                data = []
        data.append(item)
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
