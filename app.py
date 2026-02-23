import json
import streamlit as st

from glowcore.core.types import InputContext
from glowcore.core.engine import run_glow_core

st.set_page_config(page_title="GlowCore v1", page_icon="✨", layout="centered")

st.markdown("# ✨ GlowCore v1 — Decision Engine")
st.caption("Offline-first | Optional Gemini via Streamlit Secrets | Ethics gate | Memory log")

# Detect Gemini Secret
api_key = None
try:
    api_key = st.secrets.get("GEMINI_API_KEY", None)
except Exception:
    api_key = None

if api_key:
    st.success("Gemini: ✅ enabled via Secrets")
else:
    st.warning("Gemini: not set (running offline mode).")

goal = st.text_input("Mục tiêu (Goal)", value="Tăng doanh thu và tối ưu quy trình cho shop")
situation = st.text_area("Bối cảnh/Vấn đề (Situation)", value="Doanh thu giảm, ads tăng, tồn kho chậm.")
constraints = st.text_area("Ràng buộc (Constraints)", value="Ít nhân sự, ngân sách hạn chế, cần làm nhanh.")

col1, col2 = st.columns(2)
with col1:
    audience = st.selectbox("Audience", ["Business", "General", "Education", "Kids/Family"], index=0)
with col2:
    output_style = st.selectbox("Output style", ["Actionable", "Analytical", "Concise"], index=0)

use_gemini = st.checkbox("Use Gemini (if available)", value=True)

run_btn = st.button("Run GlowCore", use_container_width=True)

if run_btn:
    ctx = InputContext(
        goal=goal.strip(),
        situation=situation.strip(),
        constraints=constraints.strip(),
        audience=audience,
        output_style=output_style,
        use_gemini=use_gemini,
    )
    pack = run_glow_core(ctx, gemini_api_key=api_key)

    st.subheader("Decision Pack (Structured Output)")
    st.code(json.dumps(pack, ensure_ascii=False, indent=2), language="json")

    st.download_button(
        "⬇️ Download JSON",
        data=json.dumps(pack, ensure_ascii=False, indent=2).encode("utf-8"),
        file_name="glowcore_decision_pack.json",
        mime="application/json",
        use_container_width=True,
    )
