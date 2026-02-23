from __future__ import annotations
from typing import Optional

from glowcore.llm.providers.gemini_provider import gemini_generate

def run_llm_if_available(prompt: str, api_key: Optional[str]) -> str:
    """
    Không import ngược về core để tránh circular import.
    Trả về "" nếu không có LLM usable -> core sẽ fallback offline.
    """
    try:
        out = gemini_generate(prompt, api_key=api_key)
        return (out or "").strip()
    except Exception:
        return ""
