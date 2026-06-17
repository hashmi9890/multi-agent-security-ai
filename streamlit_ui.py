import streamlit as st
import os
from dotenv import load_dotenv
from src.orchestrator import Orchestrator

load_dotenv()

st.set_page_config(page_title="🤖 AI Agent System", page_icon="🚀", layout="wide")

st.title("🚀 AI Agent System")
st.caption("Clean Architecture • Python 3.11 • Streamlit 1.58 • Multi-Agent + Security")

with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("LLM API Key", value=os.getenv("LLM_API_KEY", ""), type="password")
    if api_key:
        st.success("✅ API Key Set")
        os.environ["LLM_API_KEY"] = api_key
    else:
        st.warning("⚠️ Add API Key in .env file")

    if st.button("🔄 Reload Agents"):
        st.cache_resource.clear()
        st.rerun()

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("**Active Agents**")
    st.caption("🔍 Research • 💻 Code • 📊 Data Analysis • 🛠️ SQL/Software")
    st.caption("🛑 Input Guard • 🛑 Output Guard")


@st.cache_resource
def get_orchestrator():
    return Orchestrator()


orchestrator = get_orchestrator()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and msg.get("agent_label"):
            st.caption(msg["agent_label"])
        st.write(msg["content"])

if prompt := st.chat_input("Ask anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤔 Routing to the right agent..."):
            result = orchestrator.handle(prompt)

        st.caption(result["agent_label"])
        st.write(result["content"])

        usage = result.get("usage")
        if usage and usage.get("total_tokens"):
            st.caption(f"🔢 Tokens — in: {usage['input_tokens']} • out: {usage['output_tokens']} • total: {usage['total_tokens']}")

        st.session_state.messages.append({
            "role": "assistant",
            "content": result["content"],
            "agent_label": result["agent_label"],
        })

st.info("💡 Multi-Agent System: Input Security → Smart Routing → Worker Agent → Output Security")