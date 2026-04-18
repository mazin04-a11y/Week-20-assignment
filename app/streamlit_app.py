"""
streamlit_app.py — The Sensory Layer (Week 17 UI Pattern).

AIOps Mission Dashboard: the user-facing interface for the R-A-R Pipeline.

UI patterns applied:
  - Week 17: st.form + st.form_submit_button (controlled submission)
  - Week 17: st.spinner — Visual Context Manager (perception of time)
  - Week 17: st.session_state — prevents variable loss on re-render
  - Week 17: st.sidebar — Configuration panel (Tier 1 widgets)
  - Week 15: try/except Immune System for graceful degradation
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.crew                 import run_crew
from src.tools.database       import setup_knowledge_db, save_run
from src.tools.debug_tools    import run_smoke_test, run_golive_checklist

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AIOps Mission Dashboard",
    page_icon="🤖",
    layout="wide",
)

# ── Session State: prevents variable loss on Streamlit re-renders (Week 17) ───
# Streamlit is stateless — every interaction re-runs the script from top.
# st.session_state persists values across runs within the same session.
if "last_result"  not in st.session_state:
    st.session_state["last_result"]  = None   # Stores last crew output
if "run_count"    not in st.session_state:
    st.session_state["run_count"]    = 0      # Tracks number of runs this session
if "last_topic"   not in st.session_state:
    st.session_state["last_topic"]   = ""     # Stores last submitted topic
if "debug_mode"   not in st.session_state:
    st.session_state["debug_mode"]   = False  # Toggle for debug panel

# ── Sidebar: Configuration panel (Week 17 — Tier 1 widgets) ──────────────────
with st.sidebar:
    st.header("⚙️ Configuration")

    st.markdown("**Pipeline Stack**")
    st.markdown("- 🧠 CrewAI R-A-R Pipeline")
    st.markdown("- 🔍 SerperDevTool (web search)")
    st.markdown("- 🗄️ SQLite (memory.db — Hard Drive)")
    st.markdown("- 🔒 SafeQueryTool (read-only guardrail)")
    st.markdown("- 📄 FileReadTool (Semantic Vault)")
    st.divider()

    st.markdown("**Architecture (Week 13/14)**")
    st.markdown("- `Process.hierarchical`")
    st.markdown("- `memory=True` (Semantic Layer)")
    st.markdown("- 3-agent crew: Research → Analyse → Write")
    st.divider()

    st.markdown("**Resilience Stack (Week 15)**")
    st.markdown("- L1: Exponential backoff retry")
    st.markdown("- L2: max_tokens=5000 cap")
    st.markdown("- L3: JSON schema enforcement")
    st.markdown("- L4: Reviewer metacognition")
    st.divider()

    # Debug mode toggle — exposes internal diagnostics (Week 16/17)
    st.session_state["debug_mode"] = st.toggle(
        "🔬 Debug Mode",
        value=st.session_state["debug_mode"],
        help="Shows execution traces, session state, and environment diagnostics."
    )

    # Session stats
    st.markdown(f"**Session runs:** {st.session_state['run_count']}")
    if st.session_state["last_topic"]:
        st.markdown(f"**Last topic:** {st.session_state['last_topic'][:40]}...")

    st.caption("Blueprint Blue · Streamlit Cloud")

# ── Main dashboard ────────────────────────────────────────────────────────────
st.title("🤖 AIOps Mission Dashboard")
st.caption("R-A-R Pipeline: Research → Analyse → Report  |  Week 18 Blueprint Blue")
st.divider()

# ── Input form (Week 17 pattern: form prevents re-run on every keystroke) ─────
with st.form("input_form"):
    user_topic = st.text_input(
        "🎯 Mission Topic",
        placeholder="e.g. AI Agentic Systems trends in 2025",
        value=st.session_state["last_topic"],
    )
    col1, col2 = st.columns([3, 1])
    with col1:
        submitted = st.form_submit_button("🚀 Run Agents", use_container_width=True)
    with col2:
        smoke_check = st.form_submit_button("🔬 Smoke Test", use_container_width=True)

# ── Smoke test runner (Week 16) ───────────────────────────────────────────────
if smoke_check:
    with st.spinner("Running environment diagnostics..."):
        results = run_smoke_test()
    passed = sum(1 for ok, _ in results.values() if ok)
    total  = len(results)
    if passed == total:
        st.success(f"✅ All {total} checks passed — ready for deployment.")
    else:
        st.warning(f"⚠️ {passed}/{total} checks passed — see console for details.")

    # Display results in an expandable table
    with st.expander("📋 Diagnostics Detail", expanded=True):
        for check, (ok, detail) in results.items():
            icon = "✅" if ok else "❌"
            st.markdown(f"{icon} **{check}** — {detail}")

# ── Mission execution ─────────────────────────────────────────────────────────
if submitted:
    if not user_topic.strip():
        st.warning("⚠️ Please enter a mission topic before running.")
    else:
        # Persist submitted topic to session state (Week 17 — stateful UI)
        st.session_state["last_topic"] = user_topic.strip()

        # Immune System: try/except for graceful degradation (Week 15)
        try:
            setup_knowledge_db()  # Ensure memory.db is ready (Week 14)

            # st.spinner — Visual Context Manager (Week 17)
            # Manages 'perception of time' during long LLM 'thinking' phases
            with st.spinner("🔍 Agents are researching... (this may take 1-3 minutes)"):
                result = run_crew(user_topic.strip())

            # Persist to session state and DB audit trail
            st.session_state["last_result"] = result
            st.session_state["run_count"]  += 1
            save_run(user_topic=user_topic.strip(), result=result, status="success")

            st.success("✅ Mission Complete!")
            st.divider()
            st.markdown("### 📋 Mission Report")
            st.markdown(result)

            # Download button for the report artifact
            st.download_button(
                label     = "📥 Download Report",
                data      = result,
                file_name = f"report_{user_topic[:30].replace(' ', '_')}.md",
                mime      = "text/markdown",
            )

        except Exception as e:
            # Graceful degradation — show error, don't crash (Week 15/17)
            save_run(user_topic=user_topic.strip(), result=str(e), status="failed")
            st.error(f"System Error: {e}")   # User-facing error message
            logger_msg = f"Streamlit mission failed for topic '{user_topic}': {e}"
            st.caption(f"Debug: {logger_msg}")  # Visible in debug mode

# ── Debug panel (Week 16/17 — session state inspection) ──────────────────────
if st.session_state["debug_mode"]:
    st.divider()
    st.markdown("### 🔬 Debug Panel")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**Session State**")
        # Exposing session state gives the 'Glass Box Experience' (Week 10)
        st.json({
            "run_count" : st.session_state["run_count"],
            "last_topic": st.session_state["last_topic"],
            "has_result": st.session_state["last_result"] is not None,
        })

    with col_b:
        st.markdown("**Environment**")
        import platform
        st.json({
            "python"   : platform.python_version(),
            "os"       : platform.system(),
            "openai_key_set"   : bool(os.environ.get("OPENAI_API_KEY")),
            "serper_key_set"   : bool(os.environ.get("SERPER_API_KEY")),
        })

    if st.session_state["last_result"]:
        with st.expander("📄 Last Raw Result"):
            st.text(st.session_state["last_result"])
