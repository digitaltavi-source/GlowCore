from __future__ import annotations
from typing import Dict, Any
import os

from glowcore.core.engine import InputContext

def gemini_decision_pack(ctx: InputContext) -> Dict[str, Any]:
    """
    Uses GEMINI_API_KEY if present. If not, raise to fallback.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")

    # Optional dependency (only works if installed)
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
Bạn là chuyên gia Decision Intelligence cho SME.
Hãy trả về JSON (không markdown) với các key:
engine_used, mode, problem_brief, root_causes (list), context_factors (list),
bottleneck, action_plan_30d (list), kpis (list), risks (list), next_step_today, ethics_notes (list).

Goal: {ctx.goal}
Situation: {ctx.situation}
Constraints: {ctx.constraints}
Audience: {ctx.audience}
Output style: {ctx.output_style}

Yêu cầu:
- Action plan phải khả thi trong 30 ngày, theo tuần.
- KPI cụ thể, đo được.
- Không gợi ý vi phạm pháp luật/phi đạo đức.
"""

    resp = model.generate_content(prompt)
    text = (resp.text or "").strip()

    # Best-effort parse: nếu không phải JSON chuẩn thì fallback lỗi để offline chạy
    import json
    data = json.loads(text)

    data["engine_used"] = "gemini"
    return data
