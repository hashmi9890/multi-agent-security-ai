import streamlit as st
import json
from datetime import datetime
from src.core.orchestrator import SecurityOrchestrator

st.set_page_config(
    page_title="🛡️ Multi-Agent Security AI",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def get_orchestrator():
    return SecurityOrchestrator()

orch = get_orchestrator()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_id" not in st.session_state:
    st.session_state.user_id = "user_" + datetime.now().strftime("%H%M%S")

# Sidebar
with st.sidebar:
    st.title("🛡️ Security AI")
    st.caption("Multi-Agent System")

    status = orch.get_system_status()
    st.metric("🤖 Active Agents", len(status["agents_loaded"]))
    st.metric("💬 Session Messages", status["memory_stats"]["total_messages"])

    st.divider()
    st.subheader("📋 Available Agents")
    for agent in status["agents_loaded"]:
        st.code(agent, language="text")

    st.divider()
    if st.button("🗑️ Clear Memory", type="secondary", use_container_width=True):
        orch.reset_memory(st.session_state.user_id)
        st.session_state.messages = []
        st.rerun()

    if st.button("💾 Download Chat", use_container_width=True):
        chat_data = json.dumps(st.session_state.messages, indent=2)
        st.download_button(
            "⬇️ Download JSON",
            chat_data,
            f"security_chat_{st.session_state.user_id}.json",
            "application/json",
            use_container_width=True
        )

# Header
st.title("🔒 Multi-Agent Security AI System")
st.caption("Threat Analysis • Vulnerability Scanning • Log Parsing • Incident Response")

# Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "meta" in msg:
            with st.expander("🔍 Agent Details"):
                st.json(msg["meta"])

# Input
if prompt := st.chat_input("Describe security concern or paste logs..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤔 Analyzing..."):
            result = orch.process(prompt, st.session_state.user_id)

        if result["status"] == "success":
            st.write(result["output"])
            meta = {
                "agent": result["agent_name"],
                "type": result["agent"],
                "confidence": result["confidence"],
                "latency": f"{result['latency_ms']}ms",
                "metadata": result.get("metadata", {})
            }
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["output"],
                "meta": meta
            })
            with st.expander("🔍 Agent Details"):
                st.json(meta)
        else:
            st.error(f"❌ Error: {result['message']}")