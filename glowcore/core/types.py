from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional, Literal, List

Audience = Literal["Business", "General", "Education", "Kids/Family"]
OutputStyle = Literal["Actionable", "Analytical", "Concise"]

@dataclass
class InputContext:
    goal: str
    situation: str
    constraints: str
    audience: Audience = "Business"
    output_style: OutputStyle = "Actionable"
    use_gemini: bool = True

DecisionPack = Dict[str, Any]
