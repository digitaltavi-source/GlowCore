import json
import streamlit as st
from glowcore.core.types import InputContext
from glowcore.core.engine import run_glow_core

st.set_page_config(page_title="GlowCore v1 — Decision Engine", page_icon="✨", layout="centered")

st.markdown("# ✨ GlowCore v1 — Decision Engine")
st.caption("Offline-first | Optional Gemini via Secrets | Ethics gate | Memory log")

# Show Gemini status
gemini_on = bool(st.secrets.get("GEMINI_API_KEY", "")) if hasattr(st, "secrets") else False
st.success("Gemini: ✅ enabled via Secrets" if gemini_on else "Gemini: ⛔ not set (offline mode)")

goal = st.text_input("Mục tiêu (Goal)", value="Tăng doanh thu và tối ưu quy trình cho shop")
situation = st.text_area("Bối cảnh/Vấn đề (Situation)", value="Doanh thu giảm, ads tăng, tồn kho chậm.")
constraints = st.text_area("Ràng buộc (Constraints)", value="Ít nhân sự, ngân sách hạn chế, cần làm nhanh.")

col1, col2 = st.columns(2)
with col1:
    audience = st.selectbox("Audience", ["Business", "General", "Education"], index=0)
with col2:
    output_style = st.selectbox("Output style", ["Actionable", "Strategic", "Detailed"], index=0)

use_llm = st.checkbox("Use Gemini (if available)", value=True)

if st.button("Run GlowCore", use_container_width=True):
    ctx = InputContext(
        goal=goal.strip(),
        situation=situation.strip(),
        constraints=constraints.strip(),
        audience=audience,
        output_style=output_style,
        use_llm=use_llm,
    )
    pack = run_glow_core(ctx)

    st.info(f"Engine used: {pack.get('engine_used')} | Mode: {pack.get('mode')}")
    st.subheader("Decision Pack (Structured Output)")
    st.json(pack)

    md = "# GlowCore Decision Pack\n\n" + "```json\n" + json.dumps(pack, ensure_ascii=False, indent=2) + "\n```\n"
    st.download_button(
        "⬇️ Download decision_pack.md",
        data=md,
        file_name="decision_pack.md",
        mime="text/markdown",
        use_container_width=True
    )
