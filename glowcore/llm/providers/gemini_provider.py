import os
from typing import Optional

def gemini_available() -> bool:
    return bool(os.environ.get("GEMINI_API_KEY"))

def gemini_generate(prompt: str) -> Optional[str]:
    # Placeholder: keep framework stable even if you haven't integrated SDK yet.
    # You can replace with google-genai later.
    if not gemini_available():
        return None
    # For now: return None to force offline path unless you implement SDK.
    return None
