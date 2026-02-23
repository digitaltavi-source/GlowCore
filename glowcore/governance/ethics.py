from __future__ import annotations
from typing import Tuple

BANNED = [
    "hack", "malware", "steal", "đánh bom", "bom", "weapon", "drugs", "ma túy"
]

def ethics_gate(text: str) -> Tuple[bool, str]:
    t = (text or "").lower()
    for w in BANNED:
        if w in t:
            return False, f"Blocked by ethics gate (keyword: {w})."
    return True, "OK"
