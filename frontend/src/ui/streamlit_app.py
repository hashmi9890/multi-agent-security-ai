import streamlit as st
import json, sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.core.orchestrator import SecurityOrchestrator

st.set_page_config(page_title="CYBERPUNK SECURITY AI", page_icon="🔐", layout="wide")

CYBERPUNK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');

.stApp {
    background: linear-gradient(135deg, #050505 0%, #0f0f1a 50%, #050505 100%);
    font-family: 'Share Tech Mono', monospace;
    color: #e0e0e0;
}

h1, h2, h3 {
    font-family: 'Orbitron', sans-serif;
    color: #00f3ff !important;
    text-shadow: 0 0 10px #00f3ff, 0 0 20px #00f3ff55;
    letter-spacing: 2px;
}

.stChatMessage {
    background: rgba(0, 243, 255, 0.05) !important;
    border-left: 3px solid #00f3ff !important;
    border-radius: 0 !important;
    margin: 8px 0 !important;
}

.stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
    border-left: 3px solid #ff00ff !important;
    background: rgba(255, 0, 255, 0.05) !important;
}

.stTextInput > div > div > input {
    background: rgba(0, 0, 0, 0.8) !important;
    border: 2px solid #00f3ff !important;
    color: #00f3ff !important;
    font-family: 'Share Tech Mono', monospace;
    border-radius: 0 !important;
    box-shadow: 0 0 10px #00f3ff22 !important;
}

.stTextInput > div > div > input:focus {
    box-shadow: 0 0 20px #00f3ff66 !important;
    border-color: #ff00ff !important;
}

.stButton > button {
    background: transparent !important;
    border: 2px solid #00f3ff !important;
    color: #00f3ff !important;
    font-family: 'Orbitron', sans-serif;
    font-weight: 700;
    border-radius: 0 !important;
    transition: all 0.3s ease;
    text-transform: uppercase;
    letter-spacing: 1px;
    width: 100%;
}

.stButton > button:hover {
    background: #00f3ff !important;
    color: #000 !important;
    box-shadow: 0 0 30px #00f3ff !important;
    transform: scale(1.05);
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #050505 0%, #1a0a2e 100%) !important;
    border-right: 2px solid #ff00ff !important;
}

.stMetric {
    background: rgba(0, 243, 255, 0.1) !important;
    border: 1px solid #00f3ff !important;
    padding: 12px !important;
    border-radius: 0 !important;
}

.stMetric-value {
    color: #ff00ff !important;
    font-family: 'Orbitron', sans-serif;
    text-shadow: 0 0 8px #ff00ff88;
}

.stMetric-label {
    color: #00f3ff !important;
    font-family: 'Share Tech Mono', monospace;
}

.streamlit-expanderHeader {
    background: rgba(255, 0, 255, 0.1) !important;
    border: 1px solid #ff00ff !important;
    border-radius: 0 !important;
    color: #ff00ff !important;
}

@keyframes glitch {
    0% { text-shadow: 2px 0 #ff00ff, -2px 0 #00f3ff; }
    25% { text-shadow: -2px 0 #ff00ff, 2px 0 #00f3ff; }
    50% { text-shadow: 2px 0 #ff00ff, -2px 0 #00f3ff; }
    75% { text-shadow: -2px 0 #ff00ff, 2px 0 #00f3ff; }
    100% { text-shadow: 2px 0 #ff00ff, -2px 0 #00f3ff; }
}

.cyber-title {
    animation: glitch 3s infinite;
}

.stCode {
    background: #000 !important;
    border: 1px solid #00f3ff !important;
    border-radius: 0 !important;
    color: #00f3ff !important;
}

.stJson {
    background: rgba(0, 0, 0, 0.8) !important;
    border: 1px solid #ff00ff !important;
    border-radius: 0 !important;
}
</style>
"""

st.markdown(CYBERPUNK_CSS, unsafe_allow_html=True)

@st.cache_resource
def get_orch():
    return SecurityOrchestrator()

orch = get_orch()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_id" not in st.session_state:
    st.session_state.user_id = "user_" + datetime.now().strftime("%H%M%S")

with st.sidebar:
    st.markdown("## SYSTEM CONTROL")
    status = orch.get_system_status()
    st.metric("MASTER AGENT", status["master_agent"]["name"])
    st.metric("SUB-AGENTS", len(status["agents_loaded"]))
    st.metric("MEMORY", status["memory_stats"]["total_messages"])
    st.markdown("---")
    st.markdown("### ACTIVE AGENTS")
    for agent in status["agents_loaded"]:
        st.code(f"> {agent}", language="text")
    st.markdown("---")
    if st.button("PURGE MEMORY", type="secondary", use_container_width=True):
        orch.reset_memory(st.session_state.user_id)
        st.session_state.messages = []
        st.rerun()

st.markdown('<h1 class="cyber-title">CYBERPUNK SECURITY AI</h1>', unsafe_allow_html=True)
st.caption("MASTER AGENT // MULTI-AGENT SYSTEM // NEURAL ACTIVE")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "meta" in msg:
            with st.expander("METADATA"):
                st.json(msg["meta"])

if prompt := st.chat_input("ENTER COMMAND"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    with st.chat_message("assistant"):
        with st.spinner("PROCESSING..."):
            result = orch.process(prompt, st.session_state.user_id)
        if result["status"] == "success":
            st.write(result["output"])
            meta = {
                "agent": result.get("agent_name", result["agent"]),
                "mode": result.get("mode", "single"),
                "latency": f"{result['latency_ms']}ms"
            }
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["output"],
                "meta": meta
            })
            with st.expander("METADATA"):
                st.json(meta)
        else:
            st.error(f"ERROR: {result['message']}")

st.markdown("---")
st.markdown("### QUICK COMMANDS")
cols = st.columns(4)
with cols[0]:
    if st.button("BROADCAST"):
        st.chat_input.value = "[TEST_ALL_AGENTS] Full scan"
with cols[1]:
    if st.button("STATUS"):
        st.chat_input.value = "[STATUS]"
with cols[2]:
    if st.button("JOBS"):
        st.chat_input.value = "Find AI security jobs"
with cols[3]:
    if st.button("INCIDENT"):
        st.chat_input.value = "Active breach response"
