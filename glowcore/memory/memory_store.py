import json
import datetime
from pathlib import Path
from typing import Dict, Any

def write_memory(record: Dict[str, Any], path: str = "memory_log.jsonl") -> None:
    p = Path(path)
    record = dict(record)
    record["_ts"] = datetime.datetime.utcnow().isoformat() + "Z"
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
