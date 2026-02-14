import json
import streamlit as st

from glowcore.core.types import InputContext
from glowcore.core.engine import run_glow_core

st.set_page_config(page_title="GlowCore v1 — Decision Engine", page_icon="✨", layout="centered")

st.markdown("# ✨ GlowCore v1 — Decision Engine")
st.caption("Offline-first | Optional Gemini via Streamlit Secrets | Ethics gate | Memory log")

# --- Gemini status (optional) ---
has_gemini = False
try:
    # Streamlit Cloud Secrets: st.secrets["GEMINI_API_KEY"]
    if "GEMINI_API_KEY" in st.secrets and str(st.secrets["GEMINI_API_KEY"]).strip():
        has_gemini = True
except Exception:
    has_gemini = False

if has_gemini:
    st.success("Gemini: ✅ enabled via Secrets")
else:
    st.info("Gemini: ⚪ not set (running offline mode)")

# --- Inputs ---
goal = st.text_input("Mục tiêu (Goal)", value="Tăng doanh thu và tối ưu quy trình cho shop")
situation = st.text_area("Bối cảnh/Vấn đề (Situation)", value="Doanh thu giảm, ads tăng, tồn kho chậm.", height=120)
constraints = st.text_area("Ràng buộc (Constraints)", value="Ít nhân sự, ngân sách hạn chế, cần làm nhanh.", height=120)

colA, colB = st.columns(2)
with colA:
    audience = st.selectbox("Audience", ["Business", "General", "Education", "Kids/Family"], index=0)
with colB:
    output_style = st.selectbox("Output style", ["Actionable", "Structured", "Deep"], index=0)

use_gemini = st.checkbox("Use Gemini (if available)", value=True)

st.markdown("---")

run_btn = st.button("Run GlowCore", use_container_width=True)

if run_btn:
    ctx = InputContext(
        goal=goal.strip(),
        situation=situation.strip(),
        constraints=constraints.strip(),
        audience=audience,
        output_style=output_style,
        use_gemini=bool(use_gemini),
    )

    pack = run_glow_core(ctx)

    st.success(f"Engine used: {pack.get('engine_used')} | Mode: {pack.get('mode')}")

    st.markdown("## Decision Pack (Structured Output)")
    st.json(pack, expanded=True)

    # ---- Download Markdown (NO triple-quote fstring -> tránh SyntaxError tuyệt đối) ----
    json_text = json.dumps(pack, ensure_ascii=False, indent=2)
    md = (
        "# GlowCore Decision Pack\n\n"
        f"**Engine:** {pack.get('engine_used')}\n\n"
        f"**Mode:** {pack.get('mode')}\n\n"
        f"**Goal:** {ctx.goal}\n\n"
        f"**Situation:** {ctx.situation}\n\n"
        f"**Constraints:** {ctx.constraints}\n\n"
        "```json\n"
        + json_text +
        "\n```\n"
    )

    st.download_button(
        "⬇️ Download decision_pack.md",
        data=md,
        file_name="decision_pack.md",
        mime="text/markdown",
        use_container_width=True,
    )
