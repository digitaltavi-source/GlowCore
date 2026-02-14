import json
import inspect
from dataclasses import asdict, is_dataclass
import streamlit as st

# Import đúng theo cấu trúc repo hiện tại của bạn
from core.engine import InputContext, run_glow_core

st.set_page_config(page_title="GlowCore v1 — Decision Engine", page_icon="✨", layout="centered")

st.markdown("# ✨ GlowCore v1 — Decision Engine")
st.caption("Offline-first | Optional Gemini via Streamlit Secrets | Ethics gate | Memory log")

# ====== Gemini status ======
def _has_gemini_key() -> bool:
    try:
        return bool(st.secrets.get("GEMINI_API_KEY", "").strip())
    except Exception:
        return False

gemini_available = _has_gemini_key()
if gemini_available:
    st.success("Gemini: ✅ enabled via Secrets")
else:
    st.warning("Gemini: not set (running offline mode). Add GEMINI_API_KEY in Streamlit Secrets to enable.")

st.markdown("---")

# ====== Inputs ======
goal = st.text_input("Mục tiêu (Goal)", value="Tăng doanh thu và tối ưu quy trình cho shop")
situation = st.text_area("Bối cảnh/Vấn đề (Situation)", value="Doanh thu giảm, ads tăng, tồn kho chậm.", height=100)
constraints = st.text_area("Ràng buộc (Constraints)", value="Ít nhân sự, ngân sách hạn chế, cần làm nhanh.", height=100)

col1, col2 = st.columns(2)
with col1:
    audience = st.selectbox("Audience", ["Business", "General", "Education"], index=0)
with col2:
    output_style = st.selectbox("Output style", ["Actionable", "Analytical", "Concise"], index=0)

use_gemini = st.checkbox("Use Gemini (if available)", value=True, disabled=not gemini_available)

st.markdown("---")

# ====== Helpers (robust adapters) ======
def _build_dataclass_kwargs(dataclass_type, raw: dict) -> dict:
    """
    Only keep keys that exist in the dataclass signature.
    Prevents TypeError if your InputContext fields change.
    """
    sig = inspect.signature(dataclass_type)
    allowed = set(sig.parameters.keys())
    return {k: v for k, v in raw.items() if k in allowed}

def _call_with_supported_kwargs(fn, raw_kwargs: dict):
    """
    Only pass kwargs that the function actually accepts.
    """
    sig = inspect.signature(fn)
    allowed = set(sig.parameters.keys())
    kw = {k: v for k, v in raw_kwargs.items() if k in allowed}
    return fn(**kw)

def _to_dict(obj):
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, dict):
        return obj
    # fallback
    try:
        return json.loads(json.dumps(obj, default=str))
    except Exception:
        return {"result": str(obj)}

# ====== Run button ======
run = st.button("Run GlowCore", use_container_width=True)

if run:
    raw_ctx = {
        "goal": goal.strip(),
        "situation": situation.strip(),
        "constraints": constraints.strip(),
        "audience": audience,
        "output_style": output_style,
        # some engines might name these differently; we still include,
        # but adapter will only pass keys that exist
        "use_gemini": bool(use_gemini and gemini_available),
        "language": "vi",
    }

    if not raw_ctx["goal"]:
        st.error("Vui lòng nhập Mục tiêu (Goal).")
        st.stop()

    # Build InputContext safely (no more mismatch)
    ctx_kwargs = _build_dataclass_kwargs(InputContext, raw_ctx)
    ctx = InputContext(**ctx_kwargs)

    # Call engine safely (only supported kwargs)
    # Some versions: run_glow_core(ctx) | others: run_glow_core(ctx, use_gemini=True)
    engine_kwargs = {
        "ctx": ctx,
        "use_gemini": bool(use_gemini and gemini_available),
    }

    try:
        result_obj = _call_with_supported_kwargs(run_glow_core, engine_kwargs)
    except TypeError:
        # fallback: simplest form
        result_obj = run_glow_core(ctx)

    result = _to_dict(result_obj)

    st.markdown("## Decision Pack (Structured Output)")

    tab1, tab2, tab3 = st.tabs(["📦 Full JSON", "✅ Action Plan", "⚠️ Risks & QC"])

    with tab1:
        st.json(result, expanded=True)

        json_bytes = json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8")
        st.download_button(
            "⬇️ Download decision_pack.json",
            data=json_bytes,
            file_name="decision_pack.json",
            mime="application/json",
            use_container_width=True,
        )

    with tab2:
        # Try to show best sections if exist
        st.subheader("Tóm tắt vấn đề")
        st.write(result.get("problem_brief", "—"))

        st.subheader("Root causes")
        rc = result.get("root_causes", [])
        if isinstance(rc, list) and rc:
            for i, x in enumerate(rc, 1):
                st.write(f"{i}. {x}")
        else:
            st.write("—")

        st.subheader("30-day plan")
        plan = result.get("action_plan_30d", [])
        if isinstance(plan, list) and plan:
            for i, x in enumerate(plan, 1):
                st.write(f"Week {i}: {x}")
        else:
            st.write("—")

        st.subheader("KPIs")
        kpis = result.get("kpis", [])
        if isinstance(kpis, list) and kpis:
            for x in kpis:
                st.write(f"- {x}")
        else:
            st.write("—")

        st.subheader("Next step today")
        st.write(result.get("next_step_today", "—"))

    with tab3:
        st.subheader("Risks")
        risks = result.get("risks", [])
        if isinstance(risks, list) and risks:
            for x in risks:
                st.write(f"- {x}")
        else:
            st.write("—")

        st.subheader("Automation opportunities")
        auto = result.get("automation_ops", [])
        if isinstance(auto, list) and auto:
            for x in auto:
                st.write(f"- {x}")
        else:
            st.write("—")

        st.subheader("Ethics notes")
        st.write(result.get("ethics_notes", "—"))

st.markdown("---")
st.markdown("### Run locally")
st.code(
    "python -m pip install -r requirements.txt\n"
    "python -m streamlit run app.py",
    language="bash",
)
st.caption("GlowCore v1 | Offline-first + Optional Gemini | Streamlit")
