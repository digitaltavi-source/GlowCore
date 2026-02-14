from __future__ import annotations
from typing import Optional, Dict, Any

from glowcore.core.engine import InputContext

def run_llm_if_available(ctx: InputContext) -> Optional[Dict[str, Any]]:
    """
    Returns dict if Gemini works; otherwise None to fall back to offline.
    """
    try:
        from glowcore.llm.providers.gemini_provider import gemini_decision_pack
        return gemini_decision_pack(ctx)
    except Exception:
        return None
