from typing import Dict, Any
from glowcore.core.types import InputContext
from glowcore.governance.ethics import ethics_gate
from glowcore.llm.router import run_llm_if_available
from glowcore.memory.memory_store import write_memory

def _offline_decision(ctx: InputContext) -> Dict[str, Any]:
    # Simple but structured, deterministic output
    return {
        "engine_used": "offline",
        "mode": "Growth" if "doanh thu" in ctx.goal.lower() else "Ops",
        "problem_brief": f"Vấn đề: {ctx.situation.strip()} | Mục tiêu: {ctx.goal.strip()}",
        "root_causes": [
            "Thiếu 1 điểm nghẽn số 1 được ưu tiên xử lý",
            "Input chưa chuẩn hoá nên process sinh lỗi/đổi hướng liên tục",
            "Thiếu KPI nhỏ để đo tiến độ mỗi tuần",
        ],
        "action_plan_30d": [
            "Week 1: Chốt 1 mục tiêu + 1 KPI chính + map quy trình hiện tại (30–60 phút).",
            "Week 2: Chuẩn hoá input (template) + giảm bước lặp thủ công.",
            "Week 3: Tự động hoá bước nhỏ (batch/auto-format/auto-report).",
            "Week 4: Review KPI + fix bottleneck lớn nhất + chuẩn hoá SOP 1 trang.",
        ],
        "kpis": ["đơn/ngày hoặc CR", "chi phí/đơn", "thời gian xử lý mỗi đơn"],
        "risks": ["Quá tham mục tiêu", "Thiếu người chịu trách nhiệm KPI", "Tự động hoá trước khi chuẩn hoá input"],
        "next_step_today": "Viết 1 câu mục tiêu + chọn 1 KPI chính, rồi liệt kê 3 bước quy trình hiện tại.",
        "ethics_notes": "Tập trung tối ưu hiệu quả bằng sản phẩm hợp pháp, có giá trị cho người dùng.",
    }

def run_glow_core(ctx: InputContext) -> Dict[str, Any]:
    ok, note = ethics_gate(ctx.goal, ctx.situation)
    if not ok:
        return {"engine_used": "ethics_gate", "status": "blocked", "message": note}

    # Optional LLM (future): if available and ctx.use_llm, try it; else fallback offline.
    llm_text = None
    if ctx.use_llm:
        prompt = f"Goal: {ctx.goal}\nSituation: {ctx.situation}\nConstraints: {ctx.constraints}\nReturn a structured decision plan."
        llm_text = run_llm_if_available(prompt)

    result = _offline_decision(ctx)
    if llm_text:
        result["engine_used"] = "gemini"
        result["llm_raw"] = llm_text

    # Memory log (never breaks app)
    try:
        write_memory({"goal": ctx.goal, "mode": result.get("mode"), "engine_used": result.get("engine_used")})
    except Exception:
        pass

    return result
