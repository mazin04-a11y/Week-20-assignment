"""
streamlit_app.py — The Sensory Layer (Week 17 UI pattern).
AIOps Mission Dashboard with sidebar configuration and form-based input.
Implements Immune System error handling for graceful degradation.
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.crew import run_crew
from src.tools.database import setup_knowledge_db, save_run

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AIOps Mission Dashboard",
    page_icon="🤖",
    layout="wide",
)

# ── Sidebar: Configuration panel ─────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")
    st.markdown("**Stack**")
    st.markdown("- 🧠 CrewAI R-A-R Pipeline")
    st.markdown("- 🔍 SerperDevTool (web search)")
    st.markdown("- 🗄️ SQLite (memory.db)")
    st.markdown("- 🔒 SafeQueryTool (read-only)")
    st.divider()
    st.markdown("**Architecture**")
    st.markdown("- `Process.hierarchical`")
    st.markdown("- Semantic Memory activated")
    st.markdown("- 3-agent crew: Research → Analyse → Write")
    st.divider()
    st.caption("Blueprint Blue · Deployed via Streamlit Cloud")

# ── Main dashboard ────────────────────────────────────────────────────────────
st.title("🤖 AIOps Mission Dashboard")
st.caption("R-A-R Pipeline: Research → Analyse → Report")
st.divider()

# ── Input form (Week 17 pattern: form + form_submit_button) ──────────────────
with st.form("input_form"):
    user_topic = st.text_input(
        "🎯 Mission Topic",
        placeholder="e.g. AI Agentic Systems trends in 2025",
    )
    submitted = st.form_submit_button("🚀 Run Agents")

# ── Mission execution ─────────────────────────────────────────────────────────
if submitted:
    if not user_topic.strip():
        st.warning("Please enter a mission topic before running.")
    else:
        # Immune System: try/except for graceful degradation
        try:
            setup_knowledge_db()  # Ensure DB is ready

            with st.spinner("🔍 Agents are researching..."):  # Managing time perception
                result = run_crew(user_topic.strip())

            # Persist the run to memory.db
            save_run(user_topic=user_topic.strip(), result=result, status="success")

            st.success("✅ Mission Complete!")
            st.divider()
            st.markdown("### 📋 Mission Report")
            st.markdown(result)

            # Download button for the report
            st.download_button(
                label="📥 Download Report",
                data=result,
                file_name=f"report_{user_topic[:30].replace(' ', '_')}.md",
                mime="text/markdown",
            )

        except Exception as e:
            save_run(user_topic=user_topic.strip(), result=str(e), status="failed")
            st.error(f"System Error: {e}")   # Graceful degradation
