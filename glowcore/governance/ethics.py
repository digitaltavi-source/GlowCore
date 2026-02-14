from __future__ import annotations
from typing import Dict, Any

def ethics_gate(goal: str, situation: str) -> Dict[str, Any]:
    """
    Simple ethics gate: block illegal/explicitly harmful intents.
    (Lightweight for demo; extend later.)
    """
    text = (goal + " " + situation).lower()

    blocked_keywords = [
        "lừa đảo", "scam", "hack", "đánh cắp", "trốn thuế", "rửa tiền",
        "thuốc cấm", "ma tuý"
    ]

    for kw in blocked_keywords:
        if kw in text:
            return {
                "allowed": False,
                "reason": f"Blocked by ethics gate keyword: {kw}",
                "notes": ["Hệ thống chỉ hỗ trợ mục tiêu hợp pháp và tạo giá trị bền vững."],
            }

    return {
        "allowed": True,
        "notes": ["Ưu tiên giải pháp hợp pháp, minh bạch, không gây hại người dùng."],
    }
