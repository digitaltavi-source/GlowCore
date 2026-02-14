from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Any, Dict

from glowcore.governance.ethics import ethics_gate
from glowcore.llm.router import run_llm_if_available
from glowcore.memory.memory_store import memory_log


@dataclass
class InputContext:
    # ✅ 3 trường cốt lõi
    goal: str
    situation: str
    constraints: str

    # ✅ fields mở rộng: có default để tránh TypeError
    audience: str = "Business"
    output_style: str = "Actionable"
    use_gemini: bool = False
    language: str = "vi"
    meta: Dict[str, Any] = field(default_factory=dict)


def _now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _detect_mode(ctx: InputContext) -> str:
    t = f"{ctx.goal} {ctx.situation} {ctx.constraints}".lower()

    growth_kw = ["doanh thu", "bán", "marketing", "ads", "quảng cáo", "conversion", "shop", "shopee", "tiktok", "funnel"]
    ops_kw = ["quy trình", "workflow", "vận hành", "sop", "kpi", "chi phí", "tự động", "automation", "process"]
    ai_kw = ["ai", "ml", "machine learning", "data", "dữ liệu", "api", "pipeline", "agent", "model"]

    if any(k in t for k in growth_kw):
        return "Growth"
    if any(k in t for k in ops_kw):
        return "Operations"
    if any(k in t for k in ai_kw):
        return "AI System"
    return "General"


def _offline_decision_pack(ctx: InputContext, mode: str) -> Dict[str, Any]:
    # Output “usable” + không chung chung quá mức
    if mode == "Growth":
        root_causes = [
            "Thiếu 1 KPI chính → không biết ưu tiên tối ưu điểm nào",
            "Input chưa chuẩn hoá nên ads/content vận hành thiếu ổn định",
            "Thiếu ‘điểm chốt’ (offer/proof/CTA) → traffic có nhưng không ra đơn đều",
        ]
        bottleneck = "Chưa có pipeline rõ (1 output chính + reverse input) nên phân tán nguồn lực."
        plan_30d = [
            "Week 1: Chốt mục tiêu + 1 KPI chính (CR hoặc đơn/ngày). Map funnel hiện tại (30–60 phút).",
            "Week 2: Chuẩn hoá input: 1 template offer + 1 template nội dung + 1 checklist QC trước khi đăng.",
            "Week 3: Batch sản xuất: 10 bài/tuần (từ 3–5 chủ đề xương sống). Test 1 biến số/lần.",
            "Week 4: Review KPI → fix bottleneck lớn nhất + chuẩn hoá SOP 1 trang.",
        ]
        automation_ops = [
            "Template input chuẩn (Notion/Sheets) → xuất báo cáo KPI tuần tự động",
            "Batch tạo outline/script/prompt pack theo chủ đề",
            "Checklist QC trước khi publish (đúng format, 1 CTA, 1 offer, 1 proof)",
        ]
        next_step = "Viết 1 câu mục tiêu + chọn 1 KPI chính, rồi liệt kê 3 bước funnel hiện tại (Hook → Offer → CTA)."

    elif mode == "Operations":
        root_causes = [
            "Quy trình chưa có Input→Process→Output rõ ràng",
            "Bước lặp thủ công nhiều nhưng chưa có template/chuẩn hoá",
            "Thiếu checklist QC nên lỗi lặp lại và tốn thời gian sửa",
        ]
        bottleneck = "Input không chuẩn → process tắc → output thiếu ổn định."
        plan_30d = [
            "Week 1: Vẽ Input→Process→Output cho 1 quy trình quan trọng nhất.",
            "Week 2: Chuẩn hoá input bằng template + naming convention.",
            "Week 3: Tự động hoá 1 bước nhỏ (batch/export/checklist).",
            "Week 4: Đo thời gian xử lý → tối ưu bottleneck → viết SOP 1 trang.",
        ]
        automation_ops = [
            "Batch export .md/.json theo template",
            "Auto naming + folder structure",
            "QC checklist: format/logic/CTA/độ rõ ràng",
        ]
        next_step = "Chọn 1 output duy nhất hôm nay, rồi viết ngược lại: cần input gì để ra output đó."

    elif mode == "AI System":
        root_causes = [
            "Chưa chốt schema đầu ra nên output khó ổn định",
            "Thiếu vòng lặp test (seed/logging) → sửa lỗi tốn thời gian",
            "Chưa module hoá generator/validator/exporter",
        ]
        bottleneck = "Thiếu output schema + validator nên kết quả khó dùng ngay."
        plan_30d = [
            "Week 1: Chốt schema đầu ra (JSON/pack).",
            "Week 2: Tách module: generator → validator → exporter.",
            "Week 3: Thêm test loop (seed) + logging lỗi.",
            "Week 4: Cắm API (tuỳ chọn) + kiểm soát chi phí/token.",
        ]
        automation_ops = [
            "Validator (QC) cho output",
            "Logging + versioning prompt/pack",
            "Export pack theo chuẩn dùng lại được",
        ]
        next_step = "Chốt 1 schema output (fields + format). Sau đó tạo validator QC 5 tiêu chí."

    else:
        root_causes = [
            "Mục tiêu chưa cụ thể (chưa đo được)",
            "Thiếu 1 bước ưu tiên hoá (làm quá nhiều thứ cùng lúc)",
            "Chưa có hành động nhỏ để bắt đầu ngay",
        ]
        bottleneck = "Thiếu mục tiêu đo được và 1 bước khởi động rõ ràng."
        plan_30d = [
            "Week 1: Chốt mục tiêu đo được + 1 KPI.",
            "Week 2: Chia thành 3 bước (Input→Process→Output).",
            "Week 3: Làm thử 1 vòng nhỏ, ghi lại lỗi.",
            "Week 4: Chuẩn hoá và lặp lại.",
        ]
        automation_ops = [
            "Template + checklist QC",
            "Batch sản xuất theo chủ đề",
            "Báo cáo KPI tuần",
        ]
        next_step = "Viết mục tiêu 1 câu + KPI 1 dòng, rồi chọn 1 output duy nhất cho hôm nay."

    return {
        "engine_used": "offline",
        "mode": mode,
        "timestamp": _now(),
        "problem_brief": f"Mục tiêu: {ctx.goal} | Vấn đề: {ctx.situation}",
        "root_causes": root_causes,
        "context_factors": [
            "Nguồn lực thực tế (nhân sự/chi phí/thời gian)",
            "Kênh bán & hành vi khách hàng",
            "Quy trình hiện tại (Input→Process→Output)",
        ],
        "bottleneck": bottleneck,
        "action_plan_30d": plan_30d,
        "kpis": ["KPI1: đơn/ngày hoặc CR", "KPI2: chi phí/đơn", "KPI3: thời gian xử lý mỗi đơn"],
        "risks": [
            "Quá tham mục tiêu (làm nhiều thứ)",
            "Thiếu người chịu trách nhiệm KPI",
            "Tự động hoá trước khi chuẩn hoá input",
        ],
        "automation_ops": automation_ops,
        "next_step_today": next_step,
        "ethics_notes": "Only propose legal, ethical, human-benefit actions.",
    }


def run_glow_core(ctx: InputContext) -> Dict[str, Any]:
    # 1) Ethics gate
    ok, note = ethics_gate(ctx.goal, ctx.situation, ctx.constraints)
    if not ok:
        result = {
            "engine_used": "blocked",
            "mode": "Blocked",
            "timestamp": _now(),
            "reason": note,
        }
        memory_log(ctx, result)
        return result

    # 2) Mode detect
    mode = _detect_mode(ctx)

    # 3) LLM optional (Gemini) — nếu không có key thì fallback offline
    if ctx.use_gemini:
        llm_result = run_llm_if_available(ctx, mode)
        if isinstance(llm_result, dict) and llm_result.get("engine_used") == "gemini":
            memory_log(ctx, llm_result)
            return llm_result

    # 4) Offline pack
    result = _offline_decision_pack(ctx, mode)
    memory_log(ctx, result)
    return result
