from __future__ import annotations
from typing import List, Tuple

def ethics_gate(text: str) -> Tuple[List[str], bool]:
    notes: List[str] = ["Ethics gate: enabled"]

    t = (text or "").lower()
    banned = ["thuốc lá", "lừa đảo", "rửa tiền", "hack", "gian lận", "ma tuý"]
    if any(k in t for k in banned):
        notes.append("Detected potentially harmful/illegal domain. Provide safe alternative only.")
        return notes, False

    notes.append("No red flags detected.")
    return notes, True
