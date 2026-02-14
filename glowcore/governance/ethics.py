def ethics_gate(text: str) -> dict:
    """
    Very simple gate (offline). You can expand later.
    Returns: {"ok": bool, "notes": list[str]}
    """
    notes = []
    t = (text or "").lower()

    # Example: block obviously illegal/unsafe intents (keep it simple)
    blocked_keywords = ["hack", "lừa đảo", "scam", "rửa tiền", "ma túy", "vũ khí"]
    if any(k in t for k in blocked_keywords):
        notes.append("Potentially harmful/illegal intent detected. Please reframe the request.")
        return {"ok": False, "notes": notes}

    notes.append("Ethics gate: OK.")
    return {"ok": True, "notes": notes}
