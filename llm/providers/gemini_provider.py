from __future__ import annotations
import json
from typing import Dict, Any

def gemini_generate_decision_pack(api_key: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    schema = {
        "mode": "Growth|Margin|Ops|Cashflow|General",
        "problem_brief": "string",
        "root_causes": ["string"],
        "context_factors": ["string"],
        "bottleneck": "string",
        "action_plan_30d": ["string"],
        "kpis": ["string"],
        "risks": ["string"],
        "automation_ops": ["string"],
        "next_step_today": "string",
    }

    prompt = f"""
Return ONLY valid JSON. No markdown.

You are GlowCore Decision Engine.
Create a specific, actionable Decision Pack.

Input payload:
{json.dumps(payload, ensure_ascii=False, indent=2)}

Rules:
- Week-based 30-day plan (Week 1..4).
- Include measurable KPIs.
- Include automation opportunities.
- Avoid financial advice (no buy/sell signals), avoid illegal/harmful guidance.

Output JSON with EXACT keys:
{json.dumps(schema, ensure_ascii=False)}
"""

    resp = model.generate_content(prompt)
    text = (resp.text or "").strip()

    try:
        data = json.loads(text)
    except Exception:
        text2 = text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text2)

    for k, v in schema.items():
        if k not in data:
            data[k] = [] if isinstance(v, list) else ""

    return data
