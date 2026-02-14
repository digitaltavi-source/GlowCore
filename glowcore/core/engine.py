from typing import Dict, Any

from glowcore.core.types import InputContext
from glowcore.governance.ethics import ethics_gate
from glowcore.memory.memory_store import write_memory

def _offline_pack(ctx: InputContext) -> Dict[str, Any]:
    # Simple mode routing
    mode = "Growth" if "doanh thu" in (ctx.goal.lower()) or "ads" in (ctx.situation.lower()) else "Ops"

    pack = {
        "engine_used": "offline",
        "mode": mode,
        "problem_brief": f"Vấn đề: {ctx.situation} | Mục tiêu: {ctx.goal}",
        "root_causes": [
            "Thiếu 1 điểm nghẽn số 1 được ưu tiên xử lý",
            "Input chưa chuẩn hoá nên process sinh lỗi/đổi hướng liên tục",
            "Thiếu KPI nhỏ để đo khiến tối ưu mù mờ",
        ],
        "context_factors": [
            "Nguồn lực thực tế (nhân sự/chi phí/thời gian)",
            "Kênh bán & hành vi khách hàng",
            "Quy trình hiện tại (Input→Process→Output)",
        ],
        "bottleneck": "Chưa có pipeline rõ (1 output chính + reverse input) nên phân tán nguồn lực.",
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
        "ethics_notes": [],
    }
    return pack

def _gemini_prompt(ctx: InputContext) -> str:
    return f"""
Bạn là cố vấn vận hành + tăng trưởng cho SME. Hãy trả về JSON ngắn gọn, thực dụng.
Goal: {ctx.goal}
Situation: {ctx.situation}
Constraints: {ctx.constraints}
Audience: {ctx.audience}
Output style: {ctx.output_style}

Yêu cầu JSON keys:
engine_used, mode, problem_brief, root_causes, bottleneck, action_plan_30d, kpis, risks, automation_ops, next_step_today
"""

def run_glow_core(ctx: InputContext) -> Dict[str, Any]:
    # Ethics gate
    gate = ethics_gate(" ".join([ctx.goal, ctx.situation, ctx.constraints]))
    if not gate["ok"]:
        return {
            "engine_used": "blocked",
            "mode": "Ethics",
            "problem_brief": "Request blocked by ethics gate.",
            "ethics_notes": gate["notes"],
        }

    # Offline baseline
    pack = _offline_pack(ctx)
    pack["ethics_notes"] = gate["notes"]

    # Optional Gemini enhancement
    if ctx.use_gemini:
        try:
            from glowcore.llm.router import run_llm_if_available
            payload = {"prompt": _gemini_prompt(ctx)}
            out = run_llm_if_available(payload)
            if out.get("ok") and out.get("text"):
                # Keep it safe: store raw LLM text as extra field
                pack["engine_used"] = "gemini"
                pack["llm_raw"] = out["text"]
        except Exception as e:
            pack["llm_error"] = str(e)

    # Memory log (optional)
    try:
        write_memory({"goal": ctx.goal, "mode": pack.get("mode"), "engine": pack.get("engine_used")})
    except Exception:
        pass

    return pack
