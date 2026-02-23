from __future__ import annotations
from typing import Dict, Any
import random
import re

from glowcore.core.types import InputContext, DecisionPack
from glowcore.governance.ethics import ethics_gate
from glowcore.llm.router import run_llm_if_available
from glowcore.memory.memory_store import write_memory

def _detect_mode(ctx: InputContext) -> str:
    t = f"{ctx.goal} {ctx.situation} {ctx.constraints}".lower()
    if re.search(r"\b(doanh thu|bán|ads|quảng cáo|conversion|khách hàng|shop|sàn|shopee|tiktok)\b", t):
        return "Growth"
    if re.search(r"\b(quy trình|workflow|process|vận hành|sop|kpi|tự động|automation|chi phí)\b", t):
        return "Operations"
    if re.search(r"\b(ai|ml|data|dữ liệu|api|pipeline|agent|hệ thống)\b", t):
        return "AI-System"
    return "General"

def _offline_pack(ctx: InputContext, mode: str) -> DecisionPack:
    # simple but usable, not one-template-only
    kpi_bank = {
        "Growth": ["CR (tỷ lệ chuyển đổi)", "Đơn/ngày", "CPA (chi phí/đơn)"],
        "Operations": ["Thời gian xử lý/đơn", "Tỷ lệ lỗi", "Chi phí vận hành"],
        "AI-System": ["Độ ổn định output", "Tỷ lệ lỗi pipeline", "Thời gian chạy"],
        "General": ["1 KPI chính", "1 KPI phụ", "1 KPI rủi ro"],
    }
    kpis = kpi_bank.get(mode, kpi_bank["General"])

    return {
        "engine_used": "offline",
        "mode": mode,
        "problem_brief": f"Mục tiêu: {ctx.goal} | Vấn đề: {ctx.situation}",
        "root_causes": [
            "Chưa chốt 1 KPI chính để ưu tiên xử lý",
            "Input thiếu chuẩn hoá nên process sinh lỗi/đổi hướng liên tục",
            "Thiếu pipeline rõ ràng (Input→Process→Output)",
        ],
        "bottleneck": "Chưa có '1 output chính' + reverse input nên phân tán nguồn lực.",
        "action_plan_30d": [
            "Week 1: Chốt 1 mục tiêu + 1 KPI chính + map quy trình hiện tại (30–60’).",
            "Week 2: Chuẩn hoá input (template) + giảm bước lặp thủ công.",
            "Week 3: Tự động hoá 1 bước nhỏ (batch/auto-format/auto-report).",
            "Week 4: Review KPI + fix bottleneck lớn nhất + chuẩn hoá SOP 1 trang.",
        ],
        "kpis": kpis,
        "risks": [
            "Quá tham mục tiêu (làm nhiều thứ)",
            "Thiếu người chịu trách nhiệm KPI",
            "Tự động hoá trước khi chuẩn hoá input",
        ],
        "automation_ops": [
            "Template input chuẩn (Notion/Sheets) → xuất báo cáo tự động",
            "Batch tạo nội dung/prompt pack theo chủ đề",
            "Auto checklist QC trước khi publish",
        ],
        "next_step_today": "Viết 1 câu mục tiêu + chọn 1 KPI chính, rồi liệt kê 3 bước quy trình hiện tại.",
        "ethics_notes": "Chỉ đề xuất tối ưu trên sản phẩm/dịch vụ tạo giá trị, không vi phạm đạo đức/pháp luật."
    }

def run_glow_core(ctx: InputContext, gemini_api_key: str | None = None) -> DecisionPack:
    ok, msg = ethics_gate(f"{ctx.goal}\n{ctx.situation}\n{ctx.constraints}")
    if not ok:
        return {"engine_used": "blocked", "reason": msg}

    mode = _detect_mode(ctx)

    # LLM path (optional)
    llm_used = False
    llm_text = ""
    if ctx.use_gemini and gemini_api_key:
        prompt = (
            "Return a concise JSON decision pack with keys: "
            "problem_brief, root_causes, bottleneck, action_plan_30d, kpis, risks, automation_ops, next_step_today.\n\n"
            f"GOAL: {ctx.goal}\nSITUATION: {ctx.situation}\nCONSTRAINTS: {ctx.constraints}\nMODE: {mode}\n"
        )
        llm_text = run_llm_if_available(prompt, gemini_api_key)
        if llm_text:
            llm_used = True

    pack = _offline_pack(ctx, mode)
    pack["engine_used"] = "gemini" if llm_used else "offline"

    write_memory({
        "goal": ctx.goal,
        "mode": mode,
        "engine_used": pack["engine_used"],
        "audience": ctx.audience,
        "output_style": ctx.output_style,
    })

    return pack
