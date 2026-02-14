import streamlit as st
from glowcore.core.engine import InputContext, run_glow_core

st.set_page_config(page_title="GlowCore v1", page_icon="✨", layout="centered")

st.markdown("# ✨ GlowCore v1 — Decision Engine")
st.caption("Offline-first | Optional Gemini via Streamlit Secrets | Ethics gate | Memory log")

# Read secrets (optional)
api_key = ""
try:
    api_key = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    api_key = ""

if api_key:
    st.success("Gemini: ✅ enabled via Secrets")
else:
    st.warning("Gemini: not set (running offline fallback). Add GEMINI_API_KEY in Streamlit Secrets for LLM mode.")

goal = st.text_input("Mục tiêu (Goal)", value="Tăng doanh thu và tối ưu quy trình cho shop")
situation = st.text_area("Bối cảnh/Vấn đề (Situation)", value="Doanh thu giảm, ads tăng, tồn kho chậm.")
constraints = st.text_area("Ràng buộc (Constraints)", value="Ít nhân sự, ngân sách hạn chế, cần làm nhanh.")

if st.button("Run GlowCore", use_container_width=True):
    ctx = InputContext(user_goal=goal, situation=situation, constraints=constraints)
    pack = run_glow_core(ctx, provider="gemini", api_key=api_key)
    st.success(f"Engine used: **{pack.engine_used}** | Mode: **{pack.mode}**")

    st.subheader("Decision Pack (Structured Output)")
    st.json(pack.__dict__)
