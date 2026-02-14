import os
import streamlit as st

# =========================
# 1) SAFE IMPORTS
# =========================
# Hỗ trợ cả 2 kiểu cấu trúc:
# - from glowcore.core.engine import ...
# - from core.engine import ...
InputContext = None
run_glow_core = None

_import_errors = []

try:
    from glowcore.core.engine import InputContext, run_glow_core  # type: ignore
except Exception as e:
    _import_errors.append(f"glowcore.core.engine: {e}")
    try:
        from core.engine import InputContext, run_glow_core  # type: ignore
    except Exception as e2:
        _import_errors.append(f"core.engine: {e2}")

# =========================
# 2) PAGE CONFIG
# =========================
st.set_page_config(
    page_title="GlowCore v1 — Decision Engine",
    page_icon="✨",
    layout="centered",
)

# =========================
# 3) HEADER / STATUS
# =========================
st.markdown("# ✨ GlowCore v1 — Decision Engine")
st.caption("Offline-first | Optional Gemini via Streamlit Secrets | Ethics gate | Memory log")

# Gemini secrets check (Streamlit Cloud: Settings → Secrets)
gemini_key = None
try:
    gemini_key = st.secrets.get("GEMINI_API_KEY", None)
except Exception:
    gemini_key = None

if gemini_key:
    st.success("Gemini: ✅ enabled via Secrets")
else:
    st.warning("Gemini: not set (running offline mode). Add GEMINI_API_KEY in Streamlit Secrets to enable LLM mode.")

# Nếu import fail thì báo rõ để bạn biết lỗi nằm ở import, không phải UI
if InputContext is None or run_glow_core is None:
    st.error("Không import được engine. Kiểm tra cấu trúc thư mục / __init__.py / đường dẫn import.")
    st.code("\n".join(_import_errors))
    st.stop()

# =========================
# 4) UTIL: SAFE GET + KEY MAP
# =========================
def pick(d: dict, *keys, default=None):
    """Lấy giá trị theo nhiều tên key khác nhau (tự động fallback)."""
    for k in keys:
        if isinstance(d, dict) and k in d and d[k] not in (None, ""):
            return d[k]
    return default

def as_list(x):
    if x is None:
        return []
    if isinstance(x, list):
        return x
    if isinstance(x, str):
        # nếu là chuỗi dài có thể tách dòng
        lines = [s.strip("-• \t") for s in x.splitlines() if s.strip()]
        return lines if lines else [x]
    return [x]

def render_bullets(items):
    for it in as_list(items):
        st.write(f"- {it}")

def normalize_result(raw: dict) -> dict:
    """Chuẩn hoá output để UI luôn render được."""
    if not isinstance(raw, dict):
        return {"raw": raw}

    return {
        "engine_used": pick(raw, "engine_used", "engine", default="offline"),
        "mode": pick(raw, "mode", "route", "detected_mode", default="General"),
        "problem_brief": pick(raw, "problem_brief", "brief", "summary", "problem", default=""),
        "root_causes": as_list(pick(raw, "root_causes", "causes", "rootcause", default=[])),
        "context_factors": as_list(pick(raw, "context_factors", "context", "factors", default=[])),
        "bottleneck": pick(raw, "bottleneck", "constraint", "key_bottleneck", default=""),
        "action_plan_30d": as_list(pick(raw, "action_plan_30d", "plan_30d", "plan", "action_plan", default=[])),
        "kpis": as_list(pick(raw, "kpis", "metrics", "success_metrics", default=[])),
        "risks": as_list(pick(raw, "risks", "risk", "risk_notes", default=[])),
        "automation_ops": as_list(pick(raw, "automation_ops", "automation", "automation_opportunities", default=[])),
        "next_step_today": pick(raw, "next_step_today", "next_step", "today", default=""),
        "ethics_notes": as_list(pick(raw, "ethics_notes", "ethics", "compliance", default=[])),
        "_raw": raw,
    }

# =========================
# 5) INPUT UI
# =========================
st.markdown("### Input")

goal = st.text_input("Mục tiêu (Goal)", value="Tăng doanh thu và tối ưu quy trình cho shop")
situation = st.text_area("Bối cảnh/Vấn đề (Situation)", value="Doanh thu giảm, ads tăng, tồn kho chậm.", height=110)
constraints = st.text_area("Ràng buộc (Constraints)", value="Ít nhân sự, ngân sách hạn chế, cần làm nhanh.", height=110)

colA, colB = st.columns(2)
with colA:
    audience = st.selectbox("Audience", ["Business", "General", "Education"], index=0)
with colB:
    output_style = st.selectbox("Output style", ["Actionable", "Strategic", "Compact"], index=0)

use_llm = st.checkbox(
    "Use Gemini (if available)",
    value=bool(gemini_key),
    help="Nếu có GEMINI_API_KEY trong Secrets thì bật được. Nếu không có thì tự chạy offline."
)

st.divider()

# =========================
# 6) RUN
# =========================
if st.button("Run GlowCore", use_container_width=True):
    if not goal.strip():
        st.error("Vui lòng nhập Mục tiêu (Goal).")
        st.stop()

    # InputContext: tuỳ code engine của bạn.
    # Mình truyền các trường phổ biến nhất — nếu engine bạn đặt tên khác,
    # phần run_glow_core vẫn có thể xử lý qua **kwargs hoặc dataclass fields.
    try:
        ctx = InputContext(
            goal=goal.strip(),
            situation=situation.strip(),
            constraints=constraints.strip(),
            audience=audience,
            output_style=output_style,
        )
    except TypeError:
        # fallback nếu InputContext ít field hơn
        ctx = InputContext(
            goal=goal.strip(),
            situation=situation.strip(),
            constraints=constraints.strip(),
        )

    # Run
    try:
        # engine có thể nhận tham số use_llm / api_key, tuỳ bạn.
        # Ta gọi theo cách an toàn: thử gọi có use_llm, nếu fail thì gọi tối giản.
        try:
            raw = run_glow_core(ctx, use_llm=use_llm)  # type: ignore
        except TypeError:
            raw = run_glow_core(ctx)  # type: ignore
    except Exception as e:
        st.error("Engine lỗi khi chạy.")
        st.exception(e)
        st.stop()

    res = normalize_result(raw)

    st.success(f"Engine used: **{res['engine_used']}** | Mode: **{res['mode']}**")

    # =========================
    # 7) EXECUTIVE REPORT VIEW
    # =========================
    st.markdown("## Decision Report")

    st.markdown("### 🔍 Problem Brief")
    if res["problem_brief"]:
        st.write(res["problem_brief"])
    else:
        st.write("—")

    st.markdown("### 🧠 Root Causes")
    if res["root_causes"]:
        render_bullets(res["root_causes"])
    else:
        st.write("—")

    st.markdown("### 🧭 Context Factors")
    if res["context_factors"]:
        render_bullets(res["context_factors"])
    else:
        st.write("—")

    st.markdown("### ⚠ Bottleneck")
    if res["bottleneck"]:
        st.warning(res["bottleneck"])
    else:
        st.write("—")

    st.markdown("### 🚀 30-Day Action Plan")
    if res["action_plan_30d"]:
        render_bullets(res["action_plan_30d"])
    else:
        st.write("—")

    st.markdown("### 📊 KPI Framework")
    if res["kpis"]:
        render_bullets(res["kpis"])
    else:
        st.write("—")

    st.markdown("### 🧱 Risks")
    if res["risks"]:
        render_bullets(res["risks"])
    else:
        st.write("—")

    st.markdown("### 🔧 Automation Opportunities")
    if res["automation_ops"]:
        render_bullets(res["automation_ops"])
    else:
        st.write("—")

    st.markdown("### ▶ Next Step Today")
    if res["next_step_today"]:
        st.success(res["next_step_today"])
    else:
        st.write("—")

    st.markdown("### ✅ Ethics Notes")
    if res["ethics_notes"]:
        render_bullets(res["ethics_notes"])
    else:
        st.write("—")

    st.divider()

    # =========================
    # 8) JSON (TECH VIEW)
    # =========================
    with st.expander("🔎 View Structured JSON"):
        st.json(res["_raw"])

# =========================
# 9) FOOTER
# =========================
st.markdown("---")
st.caption("GlowCore v1 | Decision Intelligence Demo | Streamlit App")
