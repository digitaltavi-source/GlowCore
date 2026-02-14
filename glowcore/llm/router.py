from typing import Dict, Any

from glowcore.llm.providers.gemini_provider import gemini_generate

def run_llm_if_available(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    payload: dict (no InputContext import to avoid circular imports)
    """
    return gemini_generate(payload)
