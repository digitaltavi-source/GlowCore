from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import datetime

from glowcore.governance.ethics import ethics_gate
from glowcore.memory.memory_store import MemoryStore
from glowcore.llm.router import llm_decision_pack

@dataclass
class InputContext:
    user_goal: str
    situation: str
    constraints: str = ""
    audience: str = "SME"
    domain: str = "Decision"
    language: str = "vi"

@dataclass
class DecisionPack:
    engine_used: str
    mode: str
    problem_brief: str
    root_causes: List[str]
    context_factors: List[str]
    bottleneck: str
    action_plan_30d: List[str]
    kpis: List[str]
    risks: List[str]
    automation_ops: List[str]
    next_step_today: str
    ethics_notes: List[str]
    meta: Dict[str, Any]

def detect_mode(text: str) -> str:
    t = (text or "").lower()
    if any(k in t for k in ["doanh thu", "đơn", "ads", "chuyển đổi", "shopee", "tiktok"]):
        return "Growth"
    if any(k in t for k in ["chi phí", "margin", "lợi nhuận", "giá vốn"]):
        return "Margin"
    if any(k in t for k in ["quy trình", "vận hành", "tồn kho", "giao hàng", "sop"]):
        return "Ops"
    if any(k in t for k in ["dòng tiền", "cashflow", "nợ", "thu chi"]):
        return "Cashflow"
    return "General"

def run_glow_core(ctx: InputContext, memory: Optional[MemoryStore] = None, provider: str = "gemini", api_key: str = "") -> DecisionPack:
    memory = memory or MemoryStore()

    text_all = f"{ctx.user_goal} {ctx.situation} {ctx.constraints}"
    mode = detect_mode(text_all)

    ethics_notes, allowed = ethics_gate(text_all)

    # If blocked → safe alternative
    if not allowed:
        pack = DecisionPack(
            engine_used="offline_safe",
            mode=mode,
            problem_brief=f"Vấn đề: {ctx.situation.strip()} | Mục tiêu: {ctx.user_goal.strip()}",
            root_causes=["Không hỗ trợ mục tiêu gây hại/phi pháp."],
            context_factors=["Cần chuyển sang hướng tạo giá trị lành mạnh và hợp pháp."],
            bottleneck="Định hướng hiện tại có rủi ro đạo đức/pháp lý.",
            action_plan_30d=["Xác định hướng thay thế an toàn và hợp pháp trong 7 ngày, sau đó lập kế hoạch 30 ngày."],
            kpis=["KPI: tính phù hợp pháp lý/đạo đức", "KPI: phản hồi khách hàng"],
            risks=["Rủi ro pháp lý", "Rủi ro ảnh hưởng cộng đồng"],
            automation_ops=["Tự động hoá nghiên cứu thị trường sản phẩm thay thế (an toàn)."],
            next_step_today="Viết 3 lựa chọn sản phẩm/dịch vụ thay thế không gây hại.",
            ethics_notes=ethics_notes,
            meta={"ts": datetime.datetime.now().isoformat(timespec="seconds"), "engine": "glowcore_v1"},
        )
        memory.append({"input": ctx.__dict__, "engine_used": pack.engine_used, "mode": pack.mode, "ts": pack.meta["ts"]})
        return pack

    # Try LLM if api_key exists
    llm_data = None
    engine_used = "offline"
    if api_key.strip():
        payload = {
            "user_goal": ctx.user_goal,
            "situation": ctx.situation,
            "constraints": ctx.constraints,
            "audience": ctx.audience,
            "domain": ctx.domain,
            "language": ctx.language,
        }
        llm_data, err = llm_decision_pack(provider, api_key.strip(), payload)
        if not err and llm_data:
            engine_used = "gemini"

    if llm_data:
        pack = DecisionPack(
            engine_used=engine_used,
            mode=llm_data.get("mode") or mode,
            problem_brief=llm_data.get("problem_brief", ""),
            root_causes=llm_data.get("root_causes", []),
            context_factors=llm_data.get("context_factors", []),
            bottleneck=llm_data.get("bottleneck", ""),
            action_plan_30d=llm_data.get("action_plan_30d", []),
            kpis=llm_data.get("kpis", []),
            risks=llm_data.get("risks", []),
            automation_ops=llm_data.get("automation_ops", []),
            next_step_today=llm_data.get("next_step_today", ""),
            ethics_notes=ethics_notes,
            meta={"ts": datetime.datetime.now().isoformat(timespec="seconds"), "engine": "glowcore_v1"},
        )
    else:
        # Offline fallback (still structured)
        pack = DecisionPack(
            engine_used=engine_used,
            mode=mode,
            problem_brief=f"Vấn đề: {ctx.situation.strip()} | Mục tiêu: {ctx.user_goal.strip()}",
            root_causes=[
                "Thiếu 1 điểm nghẽn số 1 được ưu tiên xử lý",
                "Input chưa chuẩn hoá nên process sinh lỗi/đổi hướng liên tục",
                "Thiếu KPI nhỏ để đo khiến tối ưu mù",
            ],
            context_factors=[
                "Nguồn lực thực tế (nhân sự/chi phí/thời gian)",
                "Kênh bán & hành vi khách hàng",
                "Quy trình hiện tại (Input→Process→Output)",
            ],
            bottleneck="Chưa có pipeline rõ (1 output chính → reverse input) nên phân tán nguồn lực.",
            action_plan_30d=[
                "Week 1: Chốt 1 mục tiêu + 1 KPI chính + map quy trình hiện tại (30–60 phút).",
                "Week 2: Chuẩn hoá input (template) + giảm bước lặp thủ công.",
                "Week 3: Tự động hoá 1 bước nhỏ (batch/auto-format/auto-report).",
                "Week 4: Review KPI + fix 1 bottleneck lớn nhất + chuẩn hoá SOP 1 trang.",
            ],
            kpis=["KPI1: đơn/ngày hoặc CR", "KPI2: chi phí/đơn", "KPI3: thời gian xử lý mỗi đơn"],
            risks=["Quá tham mục tiêu (làm nhiều thứ)", "Thiếu người chịu trách nhiệm KPI", "Tự động hoá trước khi chuẩn hoá input"],
            automation_ops=[
                "Tạo template input chuẩn (Notion/Sheets) → xuất báo cáo tự động",
                "Batch tạo content/prompt pack theo chủ đề",
                "Auto checklist QC trước khi publish",
            ],
            next_step_today="Viết 1 câu mục tiêu + chọn 1 KPI chính, rồi liệt kê 3 bước quy trình hiện tại.",
            ethics_notes=ethics_notes,
            meta={"ts": datetime.datetime.now().isoformat(timespec="seconds"), "engine": "glowcore_v1"},
        )

    memory.append({"input": ctx.__dict__, "engine_used": pack.engine_used, "mode": pack.mode, "ts": pack.meta["ts"]})
    return pack
