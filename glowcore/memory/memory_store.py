from __future__ import annotations
import json
import os
import datetime
from typing import Dict, Any

def write_memory(entry: Dict[str, Any], path: str = "memory_log.jsonl") -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    entry = dict(entry)
    entry["ts"] = datetime.datetime.utcnow().isoformat()
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
