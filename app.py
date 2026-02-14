import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import os
import sys
import json
import streamlit as st

# --- Make sure repo root is on PYTHONPATH (fix Streamlit Cloud imports) ---
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# --- Safe imports (works on Streamlit Cloud/Linux) ---
try:
    from glowcore.core.engine import InputContext, run_glow_core
except Exception as e:
    st.error("❌ Import failed: cannot load core.engine. Check folder names + __init__.py files.")
    st.code(str(e))
    st.stop()

st.set_page_config(
    page_title="GlowCore v1 — Decision Engine",
    page_icon="✨",
    layout="centered"
)

st.title("✨ GlowCore v1 — Decision Engine")
st.caption("Offline-first | Optional Gemini via Streamlit Secrets | Ethics gate | Memory log")

# --- Gemini detection (optional) ---
GEMINI_KEY = st.secrets.get("GEMINI_API_KEY", "") if hasattr(st, "secrets") else ""
gemini_ready = bool(GEMINI_KEY)

if gemini_ready:
    st.success("Gemini: ✅ enabled via Secrets")
else:
    st.warning("Gemini: not set (offline mode). Add GEMINI_API_KEY in Streamlit Secrets to enable.")

# --- Inputs ---
goal = st.text_input("Mục tiêu (Goal)", value="Tăng doanh thu và tối ưu quy trình cho shop")
situation = st.text_area("Bối cảnh/Vấn đề (Situation)", value="Doanh thu giảm, ads tăng, tồn kho chậm.", height=90)
constraints = st.text_area("Ràng buộc (Constraints)", value="Ít nhân sự, ngân sách hạn chế, cần làm nhanh.", height=90)

col1, col2 = st.columns(2)
with col1:
    audience = st.selectbox("Audience", ["Business", "General", "Education", "Kids/Family"], index=0)
with col2:
    output_style = st.selectbox("Output style", ["Actionable", "Detailed", "Compact"], index=0)

use_gemini = st.checkbox("Use Gemini (if available)", value=True)

st.divider()

run_btn = st.button("Run GlowCore", use_container_width=True)

if run_btn:
    if not goal.strip():
        st.error("Vui lòng nhập Goal.")
        st.stop()

    # --- Build context (robust to different engine signatures) ---
    # Some engine versions include more fields; we only pass the core 3 to avoid TypeError.
    ctx = InputContext(
        goal=goal.strip(),
        situation=situation.strip(),
        constraints=constraints.strip(),
    )

    try:
        result = run_glow_core(
            ctx,
            audience=audience,
            output_style=output_style,
            use_gemini=(use_gemini and gemini_ready),
        )
    except TypeError:
        # Fallback if your engine uses a different function signature
        result = run_glow_core(ctx)

    st.success("✅ Done")

    # --- Display result nicely ---
    st.subheader("Decision Pack (Structured Output)")

    # If result is dict-like
    if isinstance(result, dict):
        st.json(result)
        pack = result
    else:
        # If result is a dataclass/object, try to convert
        try:
            pack = result.__dict__
        except Exception:
            pack = {"result": str(result)}
        st.json(pack)

    # --- Download button ---
    md = "```json\n" + json.dumps(pack, ensure_ascii=False, indent=2) + "\n```"
    st.download_button(
        "⬇️ Download result (.md)",
        data=md,
        file_name="glowcore_decision_pack.md",
        mime="text/markdown",
        use_container_width=True
    )

st.divider()
st.caption("GlowCore v1 | Offline-first + optional Gemini | Streamlit Cloud ready")
