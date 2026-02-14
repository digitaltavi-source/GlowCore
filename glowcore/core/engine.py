from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List

from glowcore.governance.ethics import ethics_gate
from glowcore.llm.router import run_llm_if_available
from glowcore.memory.memory_store import append_memory


@dataclass
class InputContext:
    goal: str
    situation: str
    constraints: str
    audience: str = "Business"
    output_style: str = "Actionable"
    use_gemini: bool = False


def _offline_pack(ctx: InputContext) -> Dict[str, Any]:
    # Offline logic: stable, structured, “ăn điểm” vì rõ ràng + actionable
    mode = "Growth" if ctx.audience == "Business" else "General"

    problem_brief = f"Vấn đề: {ctx.situation} | Mục tiêu: {ctx.goal}"

    root_causes = [
        "Thiếu 1 điểm nghẽn số 1 được ưu tiên xử lý",
        "Input chưa chuẩn hoá nên process sinh lỗi/đổi hướng liên tục",
        "Thiếu KPI nhỏ để đo khiến tối ưu mù",
    ]

    context_factors = [
        "Nguồn lực thực tế (nhân sự/chi phí/thời gian)",
        "Kênh bán & hành vi khách hàng",
        "Quy trình hiện tại (Input→Process→Output)",
    ]

    bottleneck = "Chưa có pipeline rõ (1 output chính + reverse input) nên phân tán nguồn lực."

    action_plan_30d = [
        "Week 1: Chốt 1 mục tiêu + 1 KPI chính + map quy trình hiện tại (30–60 phút).",
        "Week 2: Chuẩn hoá input (template) + giảm bước lặp thủ công.",
        "Week 3: Tự động hoá 1 bước nhỏ (batch/auto-format/auto-report).",
        "Week 4: Review KPI + fix bottleneck lớn nhất + chuẩn hoá SOP 1 trang.",
    ]

    kpis = ["KPI1: đơn/ngày hoặc CR", "KPI2: chi phí/đơn", "KPI3: thời gian xử lý mỗi đơn"]
    risks = ["Quá tham mục tiêu (làm nhiều thứ)", "Thiếu người chịu trách nhiệm KPI", "Tự động hoá trước khi chuẩn hoá input"]
    automation_ops = [
        "Tạo template input chuẩn (Notion/Sheets) → xuất báo cáo tự động",
        "Batch tạo content/prompt pack theo chủ đề",
        "Auto checklist QC trước khi publish",
    ]

    next_step_today = "Viết 1 câu mục tiêu + chọn 1 KPI chính, rồi liệt kê 3 bước quy trình hiện tại."

    return {
        "engine_used": "offline",
        "mode": mode,
        "problem_brief": problem_brief,
        "root_causes": root_causes,
        "context_factors": context_factors,
        "bottleneck": bottleneck,
        "action_plan_30d": action_plan_30d,
        "kpis": kpis,
        "risks": risks,
        "automation_ops": automation_ops,
        "next_step_today": next_step_today,
        "ethics_notes": ["Only recommend legal & ethical value-creating actions."],
    }


def run_glow_core(ctx: InputContext) -> Dict[str, Any]:
    # 1) Ethics gate first
    gate = ethics_gate(ctx.goal, ctx.situation)
    if not gate["allowed"]:
        result = {
            "engine_used": "blocked",
            "reason": gate["reason"],
            "ethics_notes": gate.get("notes", []),
            "next_step_today": "Vui lòng điều chỉnh mục tiêu để phù hợp pháp luật & đạo đức.",
            "action_plan_30d": [],
            "kpis": [],
            "risks": [],
        }
        append_memory({"event": "blocked", "ctx": ctx.__dict__, "result": result})
        return result

    # 2) Try LLM if enabled; else offline
    llm_result = None
    if ctx.use_gemini:
        llm_result = run_llm_if_available(ctx)

    result = llm_result if isinstance(llm_result, dict) else _offline_pack(ctx)
    result.setdefault("ethics_notes", []).extend(gate.get("notes", []))

    # 3) Memory log
    append_memory({"event": "run", "ctx": ctx.__dict__, "result": result})
    return result
