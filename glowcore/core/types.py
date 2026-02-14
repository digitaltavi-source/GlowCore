from dataclasses import dataclass

@dataclass
class InputContext:
    goal: str
    situation: str
    constraints: str
    audience: str = "Business"
    output_style: str = "Actionable"
    use_gemini: bool = True
