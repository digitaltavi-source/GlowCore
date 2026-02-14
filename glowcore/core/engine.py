# glowcore/core/engine.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import json
import datetime

from glowcore.llm.router import run_llm_if_available
from glowcore.governance.ethics import ethics_gate
from glowcore.memory.memory_store import append_memory_log


@dataclass
class InputContext:
    goal: str
    situation: str
    constraints: str
    audience: str = "Business"
    output_style: str = "Actionable"
    use_gemini: bool = True


def _now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _offline_decision_pack(ctx: InputContext) -> Dict[str, Any]:
    # Offline heuristic pack (works without API)
    mode = "Growth" if ctx.audience == "Business" else "General"

    pack = {
        "engine_used": "offline",
        "mode": mode,
        "problem_brief": f"Mục tiêu: {ctx.goal} | Vấn đề: {ctx.situation} | Ràng buộc: {ctx.constraints}",
        "root_causes": [
            "Thiếu 1 điểm nghẽn số 1 được ưu tiên xử lý",
            "Input chưa chuẩn hoá nên process sinh lỗi/đổi hướng liên tục",
            "Thiếu KPI nhỏ để đo khiến tối ưu mù",
        ],
        "context_factors": [
            "Nguồn lực thực tế (nhân sự/chi phí/thời gian)",
            "Kênh bán & hành vi khách hàng",
            "Quy trình hiện tại (Input→Process→Output)",
        ],
        "bottleneck": "Chưa có pipeline rõ (1 output chính → reverse input) nên phân tán nguồn lực.",
        "action_plan_30d": [
            "Week 1: Chốt 1 mục tiêu + 1 KPI chính + map quy trình hiện tại (30–60 phút).",
            "Week 2: Chuẩn hoá input (template) + giảm bước lặp thủ công.",
            "Week 3: Tự động hoá 1 bước nhỏ (batch/auto-format/auto-report).",
            "Week 4: Review KPI + fix 1 bottleneck lớn nhất + chuẩn hoá SOP 1 trang.",
        ],
        "kpis": [
            "KPI1: đơn/ngày hoặc CR",
            "KPI2: chi phí/đơn",
            "KPI3: thời gian xử lý mỗi đơn",
        ],
        "risks": [
            "Quá tham mục tiêu (làm nhiều thứ)",
            "Thiếu người chịu trách nhiệm KPI",
            "Tự động hoá trước khi chuẩn hoá input",
        ],
        "automation_ops": [
            "Tạo template input chuẩn (Notion/Sheets) → xuất báo cáo tự động",
            "Batch tạo content/prompt pack theo chủ đề",
            "Auto checklist QC trước khi publish",
        ],
        "next_step_today": "Viết 1 câu mục tiêu + chọn 1 KPI chính, rồi liệt kê 3 bước quy trình hiện tại.",
        "ethics_notes": "Ưu tiên giải pháp hợp pháp, không lách luật, không gây hại sức khoẻ cộng đồng.",
        "generated_at": _now(),
    }
    return pack


def _build_prompt(ctx: InputContext) -> str:
    # Prompt đủ “pro” nhưng không quá dài
    return f"""
Bạn là SME Decision Intelligence. Hãy tạo một "Decision Pack" dạng JSON, tối đa thực tế, rõ ràng, có thể làm ngay.

YÊU CẦU:
- Luôn bắt đầu từ bottleneck số 1 (điểm nghẽn lớn nhất).
- Đề xuất kế hoạch 30 ngày (theo tuần).
- Có KPI đo lường, rủi ro, và bước làm ngay hôm nay.
- Không đưa lời khuyên vi phạm pháp luật/phi đạo đức.

INPUT:
Goal: {ctx.goal}
Situation: {ctx.situation}
Constraints: {ctx.constraints}
Audience: {ctx.audience}
Output style: {ctx.output_style}

OUTPUT JSON KEYS:
engine_used, mode, problem_brief, root_causes[], context_factors[], bottleneck,
action_plan_30d[], kpis[], risks[], automation_ops[], next_step_today, ethics_notes
""".strip()


def run_glow_core(ctx: InputContext) -> Dict[str, Any]:
    # 1) Ethics gate
    ok, note = ethics_gate(ctx.goal, ctx.situation, ctx.constraints)
    if not ok:
        pack = {
            "engine_used": "blocked",
            "mode": "EthicsGate",
            "problem_brief": "Blocked by ethics gate",
            "ethics_notes": note,
            "generated_at": _now(),
        }
        append_memory_log({"event": "blocked", "ctx": ctx.__dict__, "pack": pack})
        return pack

    # 2) Try Gemini (optional)
    if ctx.use_gemini:
        prompt = _build_prompt(ctx)
        text = run_llm_if_available(prompt)
        if text:
            # Try parse JSON safely; fallback to offline if parse fails
            try:
                data = json.loads(text)
                data["engine_used"] = "gemini"
                data["generated_at"] = _now()
                append_memory_log({"event": "gemini_ok", "ctx": ctx.__dict__, "pack": data})
                return data
            except Exception:
                pass

    # 3) Offline fallback
    pack = _offline_decision_pack(ctx)
    append_memory_log({"event": "offline_ok", "ctx": ctx.__dict__, "pack": pack})
    return pack
