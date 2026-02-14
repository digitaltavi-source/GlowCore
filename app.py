import json
import streamlit as st

# ✅ Import chuẩn theo package
try:
    from glowcore.core.engine import InputContext, run_glow_core
except Exception as e:
    st.error("❌ Import failed: cannot load glowcore. Check folder names + __init__.py files.")
    st.exception(e)
    st.stop()

st.set_page_config(page_title="GlowCore v1 — Decision Engine", page_icon="✨", layout="centered")

st.markdown("# ✨ GlowCore v1 — Decision Engine")
st.caption("Offline-first | Optional Gemini via Streamlit Secrets | Ethics gate | Memory log")

# ---- Gemini status ----
gemini_ready = bool(st.secrets.get("GEMINI_API_KEY", "").strip())
if gemini_ready:
    st.success("Gemini: ✅ enabled via Secrets")
else:
    st.info("Gemini: not set (offline mode). Add GEMINI_API_KEY in Streamlit Secrets to enable.")

# ---- Inputs ----
goal = st.text_input("Mục tiêu (Goal)", value="Tăng doanh thu và tối ưu quy trình cho shop")
situation = st.text_area("Bối cảnh/Vấn đề (Situation)", value="Doanh thu giảm, ads tăng, tồn kho chậm.")
constraints = st.text_area("Ràng buộc (Constraints)", value="Ít nhân sự, ngân sách hạn chế, cần làm nhanh.")

col1, col2 = st.columns(2)
with col1:
    audience = st.selectbox("Audience", ["Business", "General", "Education", "Kids/Family"], index=0)
with col2:
    output_style = st.selectbox("Output style", ["Actionable", "Strategic", "Concise", "Detailed"], index=0)

use_gemini = st.checkbox("Use Gemini (if available)", value=True)

run_btn = st.button("Run GlowCore", use_container_width=True)

# ---- Run ----
if run_btn:
    ctx = InputContext(
        goal=goal.strip(),
        situation=situation.strip(),
        constraints=constraints.strip(),
        audience=audience,
        output_style=output_style,
        use_gemini=(use_gemini and gemini_ready),
    )

    result = run_glow_core(ctx)

    st.markdown("---")
    st.subheader("Decision Pack (Structured Output)")
    st.code(json.dumps(result, ensure_ascii=False, indent=2), language="json")

    st.subheader("Next step (Today)")
    st.write(result.get("next_step_today", "—"))

    st.subheader("30-day action plan")
    for i, step in enumerate(result.get("action_plan_30d", []), 1):
        st.write(f"{i}. {step}")

    st.subheader("KPIs")
    for kpi in result.get("kpis", []):
        st.write(f"- {kpi}")

    st.subheader("Risks")
    for risk in result.get("risks", []):
        st.write(f"- {risk}")

    st.subheader("Ethics notes")
    for note in result.get("ethics_notes", []):
        st.write(f"- {note}")
