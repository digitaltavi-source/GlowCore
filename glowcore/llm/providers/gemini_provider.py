from typing import Dict, Any
import os

def gemini_generate(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Optional Gemini. If no key, return offline fallback.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key:
        return {"ok": False, "error": "GEMINI_API_KEY not set"}

    # Lazy import so app still runs without package if key not set
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = payload.get("prompt", "")
    resp = model.generate_content(prompt)
    text = getattr(resp, "text", "") or ""

    return {"ok": True, "text": text}
