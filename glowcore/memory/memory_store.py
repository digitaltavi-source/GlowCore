from __future__ import annotations
import json
import os
from datetime import datetime
from typing import Dict, Any

MEMORY_PATH = os.getenv("GLOW_MEMORY_PATH", "memory_log.jsonl")

def append_memory(record: Dict[str, Any]) -> None:
    record["ts"] = datetime.utcnow().isoformat()
    try:
        with open(MEMORY_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        # never crash app because of memory logging
        pass
