from typing import Optional
from glowcore.llm.providers.gemini_provider import gemini_generate

def run_llm_if_available(prompt: str) -> Optional[str]:
    return gemini_generate(prompt)
