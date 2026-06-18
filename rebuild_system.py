# rebuild_system.py
# Run this script to clean, rebuild, and upgrade your AI system

import os
import shutil
import textwrap
from pathlib import Path

# ================= CONFIGURATION =================
PROJECT_NAME = "ai_agent_system"
FILES_TO_CLEAN = [
    "memory_system.py", "prompt_engine.py", "agents_router.py",
    "orchestrator.py", "streamlit_ui.py", "requirements.txt",
    ".env", ".env.example", "chat_memory.json"
]
FOLDERS_TO_CLEAN = ["__pycache__", ".streamlit", "venv_backup"]
PATTERNS_TO_CLEAN = ["*_backup.py", "*.pyc", "* (1).py", "*_copy.py"]

# ================= CLEANUP FUNCTIONS =================
def remove_file(path: Path):
    if path.exists():
        path.unlink()
        print(f"🗑️  Removed: {path.name}")

def remove_folder(path: Path):
    if path.exists():
        shutil.rmtree(path)
        print(f"🗑️  Removed folder: {path.name}")

def clean_duplicates():
    print("\n🧹 Cleaning duplicates and old files...")
    cwd = Path.cwd()
    
    # Remove specific files
    for fname in FILES_TO_CLEAN:
        remove_file(cwd / fname)
    
    # Remove folders
    for fname in FOLDERS_TO_CLEAN:
        remove_folder(cwd / fname)
    
    # Remove patterns
    for pattern in PATTERNS_TO_CLEAN:
        for f in cwd.glob(pattern):
            remove_file(f)
    
    print("✅ Cleanup complete!\n")

# ================= FILE CONTENTS =================
def get_memory_system():
    return textwrap.dedent("""
    from dataclasses import dataclass, field
    from typing import List, Dict
    import json
    from datetime import datetime

    @dataclass
    class Message:
        role: str
        content: str
        timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    class MemorySystem:
        def __init__(self, max_history: int = 20, persist_file: str = "chat_memory.json"):
            self.history: List[Message] = []
            self.max_history = max_history
            self.persist_file = persist_file
            self.load()

        def add_message(self, role: str, content: str):
            self.history.append(Message(role=role, content=content))
            self._trim()
            self.save()

        def add_user_message(self, content: str):
            self.add_message("user", content)

        def add_agent_message(self, content: str, agent: str = "assistant"):
            self.add_message(agent, content)

        def get_context(self) -> str:
            return "\\n".join([f"{m.role}: {m.content}" for m in self.history[-self.max_history:]])

        def get_history_for_ui(self) -> List[Dict]:
            return [{"role": m.role, "content": m.content} for m in self.history]

        def clear(self):
            self.history.clear()
            self.save()

        def _trim(self):
            if len(self.history) > self.max_history:
                self.history = self.history[-self.max_history:]

        def save(self):
            try:
                data = {"history": [m.__dict__ for m in self.history]}
                with open(self.persist_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except Exception:
                pass

        def load(self):
            try:
                if os.path.exists(self.persist_file):
                    with open(self.persist_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.history = [Message(**m) for m in data.get("history", [])]
            except Exception:
                self.history = []

        def get_stats(self) -> Dict:
            return {
                "total_messages": len(self.history),
                "user_messages": sum(1 for m in self.history if m.role == "user"),
                "agent_messages": sum(1 for m in self.history if m.role != "user")
            }
    """).strip()

def get_prompt_engine():
    return textwrap.dedent("""
    from typing import Dict
    from dataclasses import dataclass

    @dataclass
    class PromptTemplate:
        system: str
        user: str

    class PromptEngine:
        TEMPLATES: Dict[str, PromptTemplate] = {
            "general": PromptTemplate(
                system="You are a helpful AI assistant. Be concise and accurate.",
                user="Context:\\n{context}\\n\\nUser: {input}\\nAssistant:"
            ),
            "coder": PromptTemplate(
                system="You are an expert Python developer. Provide clean, production-ready code with comments.",
                user="Context:\\n{context}\\n\\nRequest: {input}\\n\\nCode/Explanation:"
            ),
            "analyst": PromptTemplate(
                system="You are a data analyst. Provide insights, trends, and actionable recommendations.",
                user="Context:\\n{context}\\n\\nQuery: {input}\\n\\nAnalysis:"
            ),
            "creative": PromptTemplate(
                system="You are a creative writer. Be imaginative, engaging, and original.",
                user="Context:\\n{context}\\n\\nPrompt: {input}\\n\\nResponse:"
            )
        }

        @staticmethod
        def build(intent: str, user_input: str, context: str) -> Dict[str, str]:
            template = PromptEngine.TEMPLATES.get(intent, PromptEngine.TEMPLATES["general"])
            return {
                "system": template.system,
                "user": template.user.format(context=context, input=user_input)
            }

        @staticmethod
        def list_intents() -> list:
            return list(PromptEngine.TEMPLATES.keys())
    """).strip()

def get_agents_router():
    return textwrap.dedent("""
    import re
    from typing import Tuple
    from dataclasses import dataclass

    @dataclass
    class RoutingResult:
        intent: str
        confidence: float
        agent_name: str

    class AgentsRouter:
        KEYWORDS = {
            "coder": {
                "keywords": ["code", "python", "function", "script", "bug", "fix", "implement", "debug", "api", "class"],
                "agent": "🐍 Python Coder"
            },
            "analyst": {
                "keywords": ["analyze", "data", "chart", "stats", "report", "insight", "trend", "metrics", "dashboard"],
                "agent": "📊 Data Analyst"
            },
            "creative": {
                "keywords": ["write", "story", "poem", "creative", "blog", "content", "idea", "brainstorm"],
                "agent": "✍️ Creative Writer"
            }
        }

        @staticmethod
        def route(user_input: str) -> RoutingResult:
            text = user_input.lower()
            best_intent = "general"
            best_score = 0
            best_agent = "🤖 General Assistant"

            for intent, config in AgentsRouter.KEYWORDS.items():
                score = sum(1 for kw in config["keywords"] if kw in text)
                if score > best_score:
                    best_score = score
                    best_intent = intent
                    best_agent = config["agent"]

            confidence = min(best_score / 3, 1.0) if best_score > 0 else 0.5
            return RoutingResult(intent=best_intent, confidence=confidence, agent_name=best_agent)
    """).strip()

def get_orchestrator():
    return textwrap.dedent("""
    import os
    import time
    import logging
    from typing import Dict, Optional
    from dotenv import load_dotenv
    from memory_system import MemorySystem
    from prompt_engine import PromptEngine
    from agents_router import AgentsRouter, RoutingResult

    load_dotenv()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)

    class Orchestrator:
        def __init__(self):
            self.memory = MemorySystem()
            self.router = AgentsRouter()
            self.prompt_engine = PromptEngine()
            self.api_key = os.getenv("LLM_API_KEY", "")
            self.use_real_llm = bool(self.api_key)
            logger.info(f"Orchestrator initialized | Real LLM: {self.use_real_llm}")

        def run(self, user_input: str) -> Dict:
            start_time = time.time()
            logger.info(f"Processing: {user_input[:50]}...")

            self.memory.add_user_message(user_input)
            routing = self.router.route(user_input)
            context = self.memory.get_context()
            prompts = self.prompt_engine.build(routing.intent, user_input, context)

            if self.use_real_llm:
                response = self._call_real_llm(prompts)
            else:
                response = self._mock_llm_response(routing.intent)

            self.memory.add_agent_message(response, routing.agent_name)
            elapsed = time.time() - start_time

            result = {
                "response": response,
                "intent": routing.intent,
                "agent": routing.agent_name,
                "confidence": routing.confidence,
                "latency_ms": round(elapsed * 1000, 2),
                "system_prompt": prompts["system"],
                "user_prompt": prompts["user"]
            }
            logger.info(f"Completed in {elapsed:.2f}s | Intent: {routing.intent}")
            return result

        def _call_real_llm(self, prompts: Dict) -> str:
            try:
                import openai
                client = openai.OpenAI(api_key=self.api_key)
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": prompts["system"]},
                        {"role": "user", "content": prompts["user"]}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                return resp.choices[0].message.content
            except Exception as e:
                logger.error(f"LLM Error: {e}")
                return f"⚠️ LLM Error: {str(e)}"

        def _mock_llm_response(self, intent: str) -> str:
            time.sleep(0.3)
            mocks = {
                "coder": "```python\\n# Generated Code\\ndef solution():\\n    return 'Success!'\\n```",
                "analyst": "📈 Analysis: Key insights detected. Recommendation: Optimize workflow.",
                "creative": "✨ Here's a creative response tailored to your request!",
                "general": "✅ I've processed your request. How can I help further?"
            }
            return mocks.get(intent, "🤖 Response generated.")

        def reset(self):
            self.memory.clear()
            logger.info("Memory reset")

        def get_stats(self) -> Dict:
            return {
                "memory": self.memory.get_stats(),
                "llm_mode": "Real" if self.use_real_llm else "Mock",
                "available_intents": self.prompt_engine.list_intents()
            }
    """).strip()

def get_streamlit_ui():
    return textwrap.dedent('''
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
    ''').strip()

def get_requirements():
    return textwrap.dedent("""
    streamlit>=1.28.0
    python-dotenv>=1.0.0
    openai>=1.0.0
    """).strip()

def get_env_example():
    return textwrap.dedent("""
    # Add your LLM API key here
    # Get from: https://platform.openai.com/api-keys
    LLM_API_KEY=sk-...

    # Optional: Other providers
    # GROQ_API_KEY=gsk_...
    # ANTHROPIC_API_KEY=sk-ant-...
    """).strip()

# ================= MAIN EXECUTION =================
def create_file(name: str, content: str):
    with open(name, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✨ Created: {name}")

def main():
    print("=" * 60)
    print("🚀 AI AGENT SYSTEM - REBUILD & UPGRADE")
    print("=" * 60)

    clean_duplicates()

    print("📦 Creating upgraded files...")
    create_file("memory_system.py", get_memory_system())
    create_file("prompt_engine.py", get_prompt_engine())
    create_file("agents_router.py", get_agents_router())
    create_file("orchestrator.py", get_orchestrator())
    create_file("streamlit_ui.py", get_streamlit_ui())
    create_file("requirements.txt", get_requirements())
    create_file(".env.example", get_env_example())

    print("\\n" + "=" * 60)
    print("✅ REBUILD COMPLETE!")
    print("=" * 60)
    print("\\n📋 Next Steps:")
    print("   1. pip install -r requirements.txt")
    print("   2. cp .env.example .env")
    print("   3. Add your LLM_API_KEY in .env")
    print("   4. streamlit run streamlit_ui.py")
    print("\\n✨ Upgrades Applied:")
    print("   • Memory persistence (JSON)")
    print("   • Real LLM integration ready")
    print("   • Logging system")
    print("   • Routing confidence scores")
    print("   • Download chat history")
    print("   • Debug panels in UI")
    print("   • Auto cleanup of duplicates")
    print("=" * 60)

if __name__ == "__main__":
    main()

print("✅ rebuild_system.py created successfully!")
print("👉 Run: python rebuild_system.py")