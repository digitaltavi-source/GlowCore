from __future__ import annotations
from typing import Dict, Any, Optional, Tuple
from glowcore.llm.providers.gemini_provider import gemini_generate_decision_pack

def llm_decision_pack(
    provider: str,
    api_key: str,
    payload: Dict[str, Any],
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        if provider == "gemini":
            return gemini_generate_decision_pack(api_key, payload), None
        return None, f"Unknown provider: {provider}"
    except Exception as e:
        return None, str(e)
