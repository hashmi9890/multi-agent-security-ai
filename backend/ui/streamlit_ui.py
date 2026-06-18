import streamlit as st
from orchestrator import Orchestrator
import json

st.set_page_config(
    page_title="🚀 AI Agent System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.stChatMessage { border-radius: 10px; padding: 10px; }
.metric-card { background: #f0f2f6; padding: 15px; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_orchestrator():
    return Orchestrator()

orch = get_orchestrator()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.title("⚙️ Control Panel")

    stats = orch.get_stats()
    st.metric("🧠 Memory Messages", stats["memory"]["total_messages"])
    st.metric("🤖 LLM Mode", stats["llm_mode"])

    st.divider()

    if st.button("🗑️ Clear Memory", type="secondary", use_container_width=True):
        orch.reset()
        st.session_state.messages = []
        st.rerun()

    if st.button("💾 Download Chat", use_container_width=True):
        chat_data = json.dumps(st.session_state.messages, indent=2)
        st.download_button(
            label="⬇️ Download JSON",
            data=chat_data,
            file_name="chat_history.json",
            mime="application/json",
            use_container_width=True
        )

    st.divider()
    st.caption("Available Intents:")
    for intent in stats["available_intents"]:
        st.code(intent, language="text")

# Header
st.title("🚀 AI Agent System")
st.caption("Modular Architecture • Auto Routing • Memory Persistence • Real LLM Ready")

# Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "meta" in msg:
            with st.expander("🔍 Debug Info"):
                st.json(msg["meta"])

if prompt := st.chat_input("Ask anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            result = orch.run(prompt)

        st.write(result["response"])

        meta = {
            "agent": result["agent"],
            "intent": result["intent"],
            "confidence": f"{result['confidence']:.0%}",
            "latency": f"{result['latency_ms']}ms"
        }

        st.session_state.messages.append({
            "role": "assistant",
            "content": result["response"],
            "meta": meta
        })

        with st.expander("🔍 Debug Info"):
            st.json(meta)
            st.caption("System Prompt:")
            st.code(result["system_prompt"])