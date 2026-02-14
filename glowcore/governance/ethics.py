from typing import Tuple

def ethics_gate(goal: str, situation: str) -> Tuple[bool, str]:
    # Minimal, safe, non-judgmental gate
    text = f"{goal} {situation}".lower()
    banned = ["hack", "weapon", "fraud", "scam"]
    if any(x in text for x in banned):
        return False, "Request may involve unsafe/illegal intent. Please reframe to ethical, legal use."
    return True, "OK"
