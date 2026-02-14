# glowcore/llm/router.py
from __future__ import annotations
from typing import Optional

from glowcore.llm.providers.gemini_provider import gemini_generate


def run_llm_if_available(prompt: str, temperature: float = 0.6) -> Optional[str]:
    """
    Single responsibility:
    - Receive a plain prompt (string)
    - Try calling Gemini (if key exists)
    - Return text or None
    IMPORTANT: No importing engine/InputContext here to avoid circular imports.
    """
    try:
        text = gemini_generate(prompt=prompt, temperature=temperature)
        if not text:
            return None
        return text.strip()
    except Exception:
        return None
