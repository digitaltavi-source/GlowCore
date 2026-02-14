# app.py
import json
import streamlit as st

from glowcore.core.engine import InputContext, run_glow_core


st.set_page_config(page_title="GlowCore v1 — Decision Engine", page_icon="✨", layout="centered")

st.markdown("# ✨ GlowCore v1 — Decision Engine")
st.caption("Offline-first | Optional Gemini via Streamlit Secrets | Ethics gate | Memory log")

# Status: Gemini key exists?
has_key = False
try:
    has_key = bool(st.secrets.get("GEMINI_API_KEY", "").strip())
except Exception:
    has_key = False

if has_key:
    st.success("Gemini: ✅ enabled via Secrets")
else:
    st.info("Gemini: not set → app will run offline mode.")

goal = st.text_input("Mục tiêu (Goal)", value="Tăng doanh thu và tối ưu quy trình cho shop")
situation = st.text_area("Bối cảnh/Vấn đề (Situation)", value="Doanh thu giảm, ads tăng, tồn kho chậm.")
constraints = st.text_area("Ràng buộc (Constraints)", value="Ít nhân sự, ngân sách hạn chế, cần làm nhanh.")

col1, col2 = st.columns(2)
with col1:
    audience = st.selectbox("Audience", ["Business", "General", "Education"], index=0)
with col2:
    output_style = st.selectbox("Output style", ["Actionable", "Strategic", "Compact"], index=0)

use_gemini = st.checkbox("Use Gemini (if available)", value=True)

run_btn = st.button("Run GlowCore", use_container_width=True)

if run_btn:
    ctx = InputContext(
        goal=goal.strip(),
        situation=situation.strip(),
        constraints=constraints.strip(),
        audience=audience,
        output_style=output_style,
        use_gemini=use_gemini and has_key,
    )

    pack = run_glow_core(ctx)

    st.markdown("## Decision Pack (Structured Output)")
    st.json(pack, expanded=True)

    st.markdown("### Download (.json)")
    st.download_button(
        "⬇️ Download decision_pack.json",
        data=json.dumps(pack, ensure_ascii=False, indent=2),
        file_name="decision_pack.json",
        mime="application/json",
        use_container_width=True,
    )

    st.markdown("### Copy-friendly (Markdown)")
    md = f"""# GlowCore Decision Pack
**Engine:** {pack.get('engine_used')}
**Mode:** {pack.get('mode')}
**Goal:** {goal}
**Situation:** {situation}
**Constraints:** {constraints}

```json
{json.dumps(pack, ensure_ascii=False, indent=2)}
