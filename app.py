import json
import streamlit as st

# ✅ Import theo framework chuẩn package
from glowcore.core.engine import InputContext, run_glow_core

st.set_page_config(
    page_title="GlowCore v1 — Decision Engine",
    page_icon="✨",
    layout="centered"
)

# Optional logo (không có cũng không crash)
try:
    st.image("assets/glow_logo_hd.png", width=110)
except Exception:
    pass

st.markdown("# ✨ GlowCore v1 — Decision Engine")
st.caption("Offline-first | Optional Gemini via Streamlit Secrets | Ethics gate | Memory log")

# ====== Sidebar / Status ======
gemini_ready = bool(st.secrets.get("GEMINI_API_KEY", "").strip())
if gemini_ready:
    st.success("Gemini: ✅ enabled via Secrets")
else:
    st.warning("Gemini: not set (offline mode will be used).")

# ====== Inputs ======
goal = st.text_input("Mục tiêu (Goal)", value="Tăng doanh thu và tối ưu quy trình cho shop")
situation = st.text_area("Bối cảnh/Vấn đề (Situation)", value="Doanh thu giảm, ads tăng, tồn kho chậm.", height=90)
constraints = st.text_area("Ràng buộc (Constraints)", value="Ít nhân sự, ngân sách hạn chế, cần làm nhanh.", height=90)

col1, col2 = st.columns(2)
with col1:
    audience = st.selectbox("Audience", ["Business", "General", "Education", "Kids/Family"], index=0)
with col2:
    output_style = st.selectbox("Output style", ["Actionable", "Strategic", "Concise", "Deep"], index=0)

use_gemini = st.checkbox("Use Gemini (if available)", value=True)

st.markdown("---")
run_btn = st.button("Run GlowCore", use_container_width=True)

# ====== Run ======
if run_btn:
    ctx = InputContext(
        goal=goal.strip(),
        situation=situation.strip(),
        constraints=constraints.strip(),
        audience=audience,
        output_style=output_style,
        use_gemini=bool(use_gemini and gemini_ready),
        language="vi",
    )

    result = run_glow_core(ctx)

    st.info(f"Engine used: **{result.get('engine_used')}** | Mode: **{result.get('mode')}**")

    st.subheader("Decision Pack (Structured Output)")
    st.code(json.dumps(result, ensure_ascii=False, indent=2), language="json")

    st.subheader("Next Step (Today)")
    st.write(result.get("next_step_today", "-"))

    # Download JSON
    st.download_button(
        "⬇️ Download decision_pack.json",
        data=json.dumps(result, ensure_ascii=False, indent=2),
        file_name="decision_pack.json",
        mime="application/json",
        use_container_width=True
    )

st.markdown("---")
st.markdown("### Run locally")
st.code(
    "python -m pip install -r requirements.txt\n"
    "python -m streamlit run app.py",
    language="bash"
)

st.caption("GlowCore | Offline-first Decision Engine | Gemini optional | Python + Streamlit")
