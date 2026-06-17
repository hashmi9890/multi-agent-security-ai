#!/usr/bin/env python3
"""
Advanced Multi-Agent Security System Deployment Script
Creates professional structure, generates all files, cleans old mess.
"""

import os
import shutil
import textwrap
from pathlib import Path
from datetime import datetime

# ================= CONFIGURATION =================
PROJECT_NAME = "multi_agent_security_ai"
BACKUP_FOLDER = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

STRUCTURE = {
    "src": {
        "__init__.py": "",
        "core": {
            "__init__.py": "",
            "orchestrator.py": "ORCHESTRATOR",
            "memory.py": "MEMORY",
            "prompt_engine.py": "PROMPT_ENGINE",
            "router.py": "ROUTER",
            "config.py": "CONFIG",
            "logger.py": "LOGGER"
        },
        "agents": {
            "__init__.py": "AGENTS_INIT",
            "base_agent.py": "BASE_AGENT",
            "threat_analyzer.py": "THREAT_AGENT",
            "vulnerability_scanner.py": "VULN_AGENT",
            "log_parser.py": "LOG_AGENT",
            "incident_responder.py": "INCIDENT_AGENT"
        },
        "utils": {
            "__init__.py": "",
            "helpers.py": "HELPERS"
        },
        "ui": {
            "__init__.py": "",
            "streamlit_app.py": "STREAMLIT_UI"
        }
    },
    "tests": {
        "__init__.py": "",
        "test_agents.py": "TESTS"
    },
    "data": {
        "memory": {},
        "logs": {}
    },
    "requirements.txt": "REQUIREMENTS",
    ".env.example": "ENV_EXAMPLE",
    ".gitignore": "GITIGNORE",
    "README.md": "README",
    "run.py": "RUN_SCRIPT"
}

# ================= FILE CONTENTS =================

def get_orchestrator():
    return textwrap.dedent("""
    from typing import Dict, List, Optional
    from datetime import datetime
    import logging
    from src.core.memory import ConversationMemory
    from src.core.router import IntentRouter
    from src.core.prompt_engine import PromptEngine
    from src.agents import get_agent

    logger = logging.getLogger(__name__)

    class SecurityOrchestrator:
        def __init__(self, config: Dict = None):
            self.memory = ConversationMemory()
            self.router = IntentRouter()
            self.prompt_engine = PromptEngine()
            self.config = config or {}
            self.active_agents = {}
            self._load_agents()
            logger.info("🚀 SecurityOrchestrator initialized")

        def _load_agents(self):
            agent_types = ["threat", "vulnerability", "log", "incident"]
            for agent_type in agent_types:
                try:
                    self.active_agents[agent_type] = get_agent(agent_type)
                    logger.info(f"✅ Loaded agent: {agent_type}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load {agent_type}: {e}")

        def process(self, user_input: str, user_id: str = "default") -> Dict:
            start_time = datetime.now()
            logger.info(f"📥 Processing request from {user_id}")

            # 1. Route intent
            routing = self.router.route(user_input)
            agent_type = routing["intent"]
            confidence = routing["confidence"]

            # 2. Get agent
            agent = self.active_agents.get(agent_type)
            if not agent:
                return self._error_response(f"Agent '{agent_type}' not available")

            # 3. Build context
            context = self.memory.get_context(user_id, limit=10)
            prompt = self.prompt_engine.build(agent_type, user_input, context)

            # 4. Execute agent
            try:
                result = agent.execute(prompt, metadata={
                    "user_id": user_id,
                    "confidence": confidence,
                    "timestamp": start_time.isoformat()
                })
            except Exception as e:
                logger.error(f"❌ Agent execution failed: {e}")
                return self._error_response(str(e))

            # 5. Update memory
            self.memory.add(user_id, "user", user_input)
            self.memory.add(user_id, "assistant", result.get("output", ""))

            # 6. Build response
            elapsed = (datetime.now() - start_time).total_seconds()
            response = {
                "status": "success",
                "agent": agent_type,
                "agent_name": agent.name,
                "confidence": f"{confidence:.0%}",
                "input": user_input,
                "output": result.get("output", ""),
                "metadata": result.get("metadata", {}),
                "latency_ms": round(elapsed * 1000, 2),
                "timestamp": datetime.now().isoformat()
            }

            logger.info(f"✅ Completed in {elapsed:.2f}s | Agent: {agent_type}")
            return response

        def _error_response(self, message: str) -> Dict:
            return {
                "status": "error",
                "message": message,
                "timestamp": datetime.now().isoformat()
            }

        def get_system_status(self) -> Dict:
            return {
                "agents_loaded": list(self.active_agents.keys()),
                "memory_stats": self.memory.get_stats(),
                "available_intents": self.router.get_intents()
            }

        def reset_memory(self, user_id: str = None):
            if user_id:
                self.memory.clear_user(user_id)
            else:
                self.memory.clear_all()
            logger.info("🧹 Memory reset")
    """).strip()

def get_memory():
    return textwrap.dedent("""
    from typing import Dict, List
    from dataclasses import dataclass, field, asdict
    from datetime import datetime
    import json
    from pathlib import Path

    @dataclass
    class Message:
        role: str
        content: str
        timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    class ConversationMemory:
        def __init__(self, persist_dir: str = "data/memory", max_history: int = 50):
            self.persist_dir = Path(persist_dir)
            self.persist_dir.mkdir(parents=True, exist_ok=True)
            self.max_history = max_history
            self.sessions: Dict[str, List[Message]] = {}
            self._load_all()

        def add(self, user_id: str, role: str, content: str):
            if user_id not in self.sessions:
                self.sessions[user_id] = []
            self.sessions[user_id].append(Message(role=role, content=content))
            self._trim(user_id)
            self._save_user(user_id)

        def get_context(self, user_id: str, limit: int = 10) -> str:
            messages = self.sessions.get(user_id, [])
            recent = messages[-limit:]
            return "\\n".join([f"{m.role}: {m.content}" for m in recent])

        def get_history(self, user_id: str) -> List[Dict]:
            return [asdict(m) for m in self.sessions.get(user_id, [])]

        def clear_user(self, user_id: str):
            self.sessions.pop(user_id, None)
            self._delete_user_file(user_id)

        def clear_all(self):
            self.sessions.clear()
            for f in self.persist_dir.glob("*.json"):
                f.unlink()

        def get_stats(self) -> Dict:
            return {
                "active_sessions": len(self.sessions),
                "total_messages": sum(len(m) for m in self.sessions.values())
            }

        def _trim(self, user_id: str):
            if len(self.sessions[user_id]) > self.max_history:
                self.sessions[user_id] = self.sessions[user_id][-self.max_history:]

        def _save_user(self, user_id: str):
            try:
                file_path = self.persist_dir / f"{user_id}.json"
                data = {"messages": [asdict(m) for m in self.sessions[user_id]]}
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except Exception:
                pass

        def _load_all(self):
            for file_path in self.persist_dir.glob("*.json"):
                user_id = file_path.stem
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.sessions[user_id] = [Message(**m) for m in data.get("messages", [])]
                except Exception:
                    pass

        def _delete_user_file(self, user_id: str):
            try:
                file_path = self.persist_dir / f"{user_id}.json"
                if file_path.exists():
                    file_path.unlink()
            except Exception:
                pass
    """).strip()

def get_prompt_engine():
    return textwrap.dedent("""
    from typing import Dict
    from dataclasses import dataclass

    @dataclass
    class SecurityPrompt:
        system: str
        user_template: str

    class PromptEngine:
        PROMPTS: Dict[str, SecurityPrompt] = {
            "threat": SecurityPrompt(
                system="You are a Threat Intelligence Agent. Analyze inputs for security threats, malware indicators, and attack patterns. Provide severity assessment and mitigation steps.",
                user_template="Context:\\n{context}\\n\\nThreat Query: {input}\\n\\nAnalysis:"
            ),
            "vulnerability": SecurityPrompt(
                system="You are a Vulnerability Assessment Agent. Identify security weaknesses, CVEs, and misconfigurations. Provide risk scores and remediation guidance.",
                user_template="Context:\\n{context}\\n\\nVulnerability Check: {input}\\n\\nAssessment:"
            ),
            "log": SecurityPrompt(
                system="You are a Log Analysis Agent. Parse security logs, detect anomalies, and correlate events. Highlight suspicious activities.",
                user_template="Context:\\n{context}\\n\\nLog Data: {input}\\n\\nFindings:"
            ),
            "incident": SecurityPrompt(
                system="You are an Incident Response Agent. Provide actionable steps for security incidents. Follow IR playbook: Detect, Analyze, Contain, Eradicate, Recover.",
                user_template="Context:\\n{context}\\n\\nIncident: {input}\\n\\nResponse Plan:"
            ),
            "general": SecurityPrompt(
                system="You are a Security Assistant. Provide accurate, concise security information. When unsure, recommend consulting specialized agents.",
                user_template="Context:\\n{context}\\n\\nQuery: {input}\\n\\nResponse:"
            )
        }

        @staticmethod
        def build(intent: str, user_input: str, context: str = "") -> Dict[str, str]:
            prompt = PromptEngine.PROMPTS.get(intent, PromptEngine.PROMPTS["general"])
            return {
                "system": prompt.system,
                "user": prompt.user_template.format(context=context or "No prior context", input=user_input)
            }

        @staticmethod
        def list_intents() -> list:
            return list(PromptEngine.PROMPTS.keys())
    """).strip()

def get_router():
    return textwrap.dedent("""
    import re
    from typing import Dict, List
    from dataclasses import dataclass

    @dataclass
    class RoutingResult:
        intent: str
        confidence: float
        keywords_matched: List[str]

    class IntentRouter:
        KEYWORDS = {
            "threat": ["threat", "malware", "attack", "virus", "ransomware", "phishing", "intrusion", "ioc", "indicator"],
            "vulnerability": ["vulnerability", "cve", "weakness", "patch", "exploit", "misconfiguration", "risk", "scan"],
            "log": ["log", "event", "audit", "siem", "anomaly", "suspicious", "alert", "correlation"],
            "incident": ["incident", "breach", "response", "contain", "eradicate", "recover", "playbook", "ir"]
        }

        @staticmethod
        def route(user_input: str) -> Dict:
            text = user_input.lower()
            best_intent = "general"
            best_score = 0
            matched_keywords = []

            for intent, keywords in IntentRouter.KEYWORDS.items():
                matches = [kw for kw in keywords if kw in text]
                score = len(matches)
                if score > best_score:
                    best_score = score
                    best_intent = intent
                    matched_keywords = matches

            confidence = min(best_score / 3, 1.0) if best_score > 0 else 0.5
            return {
                "intent": best_intent,
                "confidence": confidence,
                "keywords_matched": matched_keywords
            }

        @staticmethod
        def get_intents() -> list:
            return list(IntentRouter.KEYWORDS.keys()) + ["general"]
    """).strip()

def get_base_agent():
    return textwrap.dedent("""
    from abc import ABC, abstractmethod
    from typing import Dict, Any
    import logging
    from datetime import datetime

    logger = logging.getLogger(__name__)

    class BaseAgent(ABC):
        def __init__(self, name: str, agent_type: str):
            self.name = name
            self.agent_type = agent_type
            self.created_at = datetime.now().isoformat()
            logger.info(f"🤖 Initialized agent: {name} ({agent_type})")

        @abstractmethod
        def execute(self, prompt: Dict[str, str], metadata: Dict = None) -> Dict[str, Any]:
            pass

        def _build_response(self, output: str, metadata: Dict = None) -> Dict:
            return {
                "output": output,
                "agent": self.name,
                "type": self.agent_type,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }

        def get_info(self) -> Dict:
            return {
                "name": self.name,
                "type": self.agent_type,
                "created_at": self.created_at
            }
    """).strip()

def get_threat_agent():
    return textwrap.dedent("""
    from src.agents.base_agent import BaseAgent
    from typing import Dict, Any
    import re

    class ThreatAnalyzerAgent(BaseAgent):
        def __init__(self):
            super().__init__("ThreatAnalyzer", "threat")
            self.threat_db = {
                "ransomware": {"severity": "CRITICAL", "type": "Malware", "mitigation": "Isolate systems, restore from backup"},
                "phishing": {"severity": "HIGH", "type": "Social Engineering", "mitigation": "User training, email filtering"},
                "sql_injection": {"severity": "CRITICAL", "type": "Web Attack", "mitigation": "Input validation, parameterized queries"},
                "xss": {"severity": "HIGH", "type": "Web Attack", "mitigation": "Output encoding, CSP headers"}
            }

        def execute(self, prompt: Dict[str, str], metadata: Dict = None) -> Dict[str, Any]:
            user_input = prompt.get("user", "")
            findings = []
            detected_threats = []

            for threat, info in self.threat_db.items():
                if threat in user_input.lower():
                    detected_threats.append(threat)
                    findings.append({
                        "threat": threat,
                        "severity": info["severity"],
                        "type": info["type"],
                        "mitigation": info["mitigation"]
                    })

            if not detected_threats:
                output = "🔍 No known threat indicators detected. Continue monitoring."
            else:
                output = f"⚠️ THREAT DETECTED: {', '.join(detected_threats)}\\n\\n"
                for f in findings:
                    output += f"📌 {f['threat'].upper()}\\n"
                    output += f"   Severity: {f['severity']}\\n"
                    output += f"   Type: {f['type']}\\n"
                    output += f"   Mitigation: {f['mitigation']}\\n\\n"
                output += "🚨 Recommended: Isolate affected systems and initiate incident response."

            return self._build_response(output, {
                "detected_threats": detected_threats,
                "count": len(detected_threats),
                **(metadata or {})
            })
    """).strip()

def get_vuln_agent():
    return textwrap.dedent("""
    from src.agents.base_agent import BaseAgent
    from typing import Dict, Any

    class VulnerabilityScannerAgent(BaseAgent):
        def __init__(self):
            super().__init__("VulnScanner", "vulnerability")
            self.cve_db = {
                "cve-2024-0001": {"severity": 9.8, "description": "Critical RCE vulnerability", "patch": "Update to v2.1.5"},
                "cve-2024-0002": {"severity": 7.5, "description": "Authentication bypass", "patch": "Apply security patch SP3"}
            }

        def execute(self, prompt: Dict[str, str], metadata: Dict = None) -> Dict[str, Any]:
            user_input = prompt.get("user", "")
            findings = []

            for cve, info in self.cve_db.items():
                if cve.lower() in user_input.lower():
                    findings.append({
                        "cve": cve,
                        "severity": info["severity"],
                        "description": info["description"],
                        "patch": info["patch"]
                    })

            if not findings:
                output = "✅ No known CVEs detected in scan. System appears secure."
            else:
                output = "🔴 VULNERABILITIES FOUND:\\n\\n"
                for f in findings:
                    output += f"📌 {f['cve'].upper()}\\n"
                    output += f"   Severity Score: {f['severity']}/10\\n"
                    output += f"   Description: {f['description']}\\n"
                    output += f"   Remediation: {f['patch']}\\n\\n"
                output += "⚡ Action Required: Apply patches immediately."

            return self._build_response(output, {
                "vulnerabilities_found": len(findings),
                "cves": [f["cve"] for f in findings],
                **(metadata or {})
            })
    """).strip()

def get_log_agent():
    return textwrap.dedent("""
    from src.agents.base_agent import BaseAgent
    from typing import Dict, Any
    import re

    class LogParserAgent(BaseAgent):
        def __init__(self):
            super().__init__("LogParser", "log")
            self.patterns = {
                "failed_login": r"failed.?login|authentication.?fail",
                "privilege_escalation": r"privilege.?escalat|sudo|admin.?access",
                "data_exfil": r"exfil|large.?transfer|unusual.?outbound"
            }

        def execute(self, prompt: Dict[str, str], metadata: Dict = None) -> Dict[str, Any]:
            user_input = prompt.get("user", "")
            alerts = []

            for alert_type, pattern in self.patterns.items():
                if re.search(pattern, user_input, re.IGNORECASE):
                    alerts.append(alert_type)

            if not alerts:
                output = "📊 Log analysis complete. No anomalies detected."
            else:
                output = "🚨 ANOMALIES DETECTED IN LOGS:\\n\\n"
                for alert in alerts:
                    output += f"⚠️ {alert.replace('_', ' ').title()}\\n"
                output += "\\n🔍 Recommended: Investigate flagged events immediately."

            return self._build_response(output, {
                "alerts": alerts,
                "alert_count": len(alerts),
                **(metadata or {})
            })
    """).strip()

def get_incident_agent():
    return textwrap.dedent("""
    from src.agents.base_agent import BaseAgent
    from typing import Dict, Any

    class IncidentResponderAgent(BaseAgent):
        def __init__(self):
            super().__init__("IncidentResponder", "incident")
            self.playbook = {
                "containment": ["Isolate affected systems", "Block malicious IPs", "Disable compromised accounts"],
                "eradication": ["Remove malware", "Patch vulnerabilities", "Reset credentials"],
                "recovery": ["Restore from clean backup", "Verify system integrity", "Monitor for recurrence"]
            }

        def execute(self, prompt: Dict[str, str], metadata: Dict = None) -> Dict[str, Any]:
            user_input = prompt.get("user", "")
            output = "📋 INCIDENT RESPONSE PLAYBOOK\\n\\n"

            for phase, steps in self.playbook.items():
                output += f"🔹 {phase.upper()}\\n"
                for i, step in enumerate(steps, 1):
                    output += f"   {i}. {step}\\n"
                output += "\\n"

            output += "📞 Escalation: Contact SOC team if severity is HIGH or CRITICAL."

            return self._build_response(output, {
                "phases": list(self.playbook.keys()),
                **(metadata or {})
            })
    """).strip()

def get_agents_init():
    return textwrap.dedent("""
    from src.agents.threat_analyzer import ThreatAnalyzerAgent
    from src.agents.vulnerability_scanner import VulnerabilityScannerAgent
    from src.agents.log_parser import LogParserAgent
    from src.agents.incident_responder import IncidentResponderAgent

    AGENT_REGISTRY = {
        "threat": ThreatAnalyzerAgent,
        "vulnerability": VulnerabilityScannerAgent,
        "log": LogParserAgent,
        "incident": IncidentResponderAgent
    }

    def get_agent(agent_type: str):
        agent_class = AGENT_REGISTRY.get(agent_type)
        if not agent_class:
            raise ValueError(f"Unknown agent type: {agent_type}")
        return agent_class()

    __all__ = ["get_agent", "AGENT_REGISTRY"]
    """).strip()

def get_streamlit_ui():
    return textwrap.dedent("""
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
    """).strip()

def get_run_script():
    return textwrap.dedent("""
    #!/usr/bin/env python3
    from src.ui.streamlit_app import run_app

    if __name__ == "__main__":
        run_app()
    """).strip()

def get_requirements():
    return textwrap.dedent("""
    streamlit>=1.28.0
    python-dotenv>=1.0.0
    openai>=1.0.0
    pydantic>=2.0.0
    loguru>=0.7.0
    """).strip()

def get_env_example():
    return textwrap.dedent("""
    LLM_API_KEY=your_openai_api_key_here
    LOG_LEVEL=INFO
    MAX_MEMORY_HISTORY=50
    """).strip()

def get_gitignore():
    return textwrap.dedent("""
    __pycache__/
    *.pyc
    *.pyo
    .venv/
    venv/
    .env
    data/memory/*.json
    data/logs/
    *.log
    .streamlit/
    backup_*/
    .DS_Store
    """).strip()

def get_readme():
    return textwrap.dedent("""
    # 🛡️ Multi-Agent Security AI System

    Advanced security analysis platform with specialized AI agents for threat detection, vulnerability assessment, log analysis, and incident response.

    ## 🚀 Features

    - **Multi-Agent Architecture**: Specialized agents for different security domains
    - **Intelligent Routing**: Automatic intent detection and agent selection
    - **Persistent Memory**: Conversation history with JSON persistence
    - **Streamlit UI**: Interactive web interface with debug panels
    - **Production Ready**: Logging, error handling, type hints

    ## 📁 Structure

    ```
    multi_agent_security_ai/
    ├── src/
    │   ├── core/          # Orchestrator, memory, router, prompts
    │   ├── agents/        # Security agents (threat, vuln, log, incident)
    │   ├── ui/           # Streamlit interface
    │   └── utils/        # Helpers, config
    ├── tests/            # Test suite
    ├── data/             # Memory persistence, logs
    └── requirements.txt
    ```

    ## 🛠️ Setup

    ```bash
    # 1. Create virtual environment
    python -m venv .venv
    source .venv/bin/activate  # Windows: .venv\\Scripts\\activate

    # 2. Install dependencies
    pip install -r requirements.txt

    # 3. Configure environment
    cp .env.example .env
    # Edit .env with your API keys

    # 4. Run application
    streamlit run src/ui/streamlit_app.py
    ```

    ## 🤖 Agents

    | Agent | Purpose |
    |-------|---------|
    | ThreatAnalyzer | Detect malware, attacks, IOCs |
    | VulnScanner | Identify CVEs, weaknesses |
    | LogParser | Parse logs, detect anomalies |
    | IncidentResponder | IR playbook, response steps |

    ## 📝 Usage Examples

    ```
    "Analyze this log for suspicious activity: [paste log]"
    "Check for CVE-2024-0001 vulnerability"
    "Detected ransomware attack, what should I do?"
    "Failed login attempts from IP 192.168.1.100"
    ```

    ## 🔒 Security Note

    This system is for defensive security analysis. Ensure proper authorization before scanning systems.

    ## 📄 License

    MIT License
    """).strip()

def get_tests():
    return textwrap.dedent("""
    import pytest
    from src.core.orchestrator import SecurityOrchestrator

    def test_orchestrator_init():
        orch = SecurityOrchestrator()
        assert orch is not None

    def test_threat_agent():
        orch = SecurityOrchestrator()
        result = orch.process("Detected ransomware attack")
        assert result["status"] == "success"
        assert result["agent"] == "threat"
    """).strip()

def get_helpers():
    return textwrap.dedent("""
    from typing import Any
    import json

    def safe_json_dumps(obj: Any, indent: int = 2) -> str:
        try:
            return json.dumps(obj, indent=indent, default=str)
        except Exception:
            return str(obj)
    """).strip()

def get_config():
    return textwrap.dedent("""
    from dataclasses import dataclass
    import os
    from dotenv import load_dotenv

    load_dotenv()

    @dataclass
    class Config:
        LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
        LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
        MAX_MEMORY_HISTORY: int = int(os.getenv("MAX_MEMORY_HISTORY", "50"))
        PERSIST_DIR: str = "data/memory"
    """).strip()

def get_logger():
    return textwrap.dedent("""
    import logging
    import sys
    from pathlib import Path

    def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))

        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger
    """).strip()

# ================= CONTENT MAP =================
CONTENT_MAP = {
    "ORCHESTRATOR": get_orchestrator,
    "MEMORY": get_memory,
    "PROMPT_ENGINE": get_prompt_engine,
    "ROUTER": get_router,
    "BASE_AGENT": get_base_agent,
    "THREAT_AGENT": get_threat_agent,
    "VULN_AGENT": get_vuln_agent,
    "LOG_AGENT": get_log_agent,
    "INCIDENT_AGENT": get_incident_agent,
    "AGENTS_INIT": get_agents_init,
    "STREAMLIT_UI": get_streamlit_ui,
    "REQUIREMENTS": get_requirements,
    "ENV_EXAMPLE": get_env_example,
    "GITIGNORE": get_gitignore,
    "README": get_readme,
    "RUN_SCRIPT": get_run_script,
    "TESTS": get_tests,
    "HELPERS": get_helpers,
    "CONFIG": get_config,
    "LOGGER": get_logger
}

# ================= DEPLOYMENT FUNCTIONS =================

def create_backup():
    print(f"📦 Creating backup: {BACKUP_FOLDER}")
    backup_path = Path(BACKUP_FOLDER)
    backup_path.mkdir(exist_ok=True)

    for item in Path(".").iterdir():
        if item.name in [BACKUP_FOLDER, "deploy_advanced_system.py", ".git"]:
            continue
        if item.is_file():
            shutil.copy2(item, backup_path / item.name)
        elif item.is_dir():
            shutil.copytree(item, backup_path / item.name, dirs_exist_ok=True)

    print(f"✅ Backup created in {BACKUP_FOLDER}/")

def clean_old_files():
    print("🧹 Cleaning old files...")
    patterns = ["*.pyc", "__pycache__", "*.log", ".streamlit"]
    for pattern in patterns:
        for item in Path(".").rglob(pattern):
            try:
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            except Exception:
                pass
    print("✅ Cleanup complete")

def create_structure():
    print("📁 Creating advanced structure...")
    for path, content in STRUCTURE.items():
        if isinstance(content, dict):
            create_structure_recursive(Path(path), content)
        else:
            create_file(Path(path), content)
    print("✅ Structure created")

def create_structure_recursive(base: Path, structure: dict):
    base.mkdir(parents=True, exist_ok=True)
    for name, content in structure.items():
        full_path = base / name
        if isinstance(content, dict):
            create_structure_recursive(full_path, content)
        else:
            create_file(full_path, content)

def create_file(path: Path, content_key: str):
    if content_key in CONTENT_MAP:
        content = CONTENT_MAP[content_key]()
    elif content_key == "":
        content = ""
    else:
        content = content_key

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✨ Created: {path}")

def print_summary():
    print("\\n" + "=" * 60)
    print("🚀 DEPLOYMENT COMPLETE!")
    print("=" * 60)
    print("\\n✅ What's Done:")
    print("   • Advanced multi-agent architecture created")
    print("   • 4 Security agents: Threat, Vuln, Log, Incident")
    print("   • Persistent memory with JSON storage")
    print("   • Intelligent routing system")
    print("   • Professional Streamlit UI")
    print("   • Logging, config, error handling")
    print("   • Backup saved in backup_*/ folder")
    print("\\n📋 Next Steps:")
    print("   1. pip install -r requirements.txt")
    print("   2. cp .env.example .env")
    print("   3. Add LLM_API_KEY in .env")
    print("   4. streamlit run src/ui/streamlit_app.py")
    print("\\n🔗 GitHub Commands:")
    print("   rm -rf .git")
    print("   git init")
    print("   git add .")
    print("   git commit -m 'Initial: Advanced Multi-Agent Security AI'")
    print("   git branch -M main")
    print("   git remote add origin <YOUR_NEW_REPO_URL>")
    print("   git push -u origin main")
    print("=" * 60)

def main():
    print("=" * 60)
    print("🚀 ADVANCED MULTI-AGENT SECURITY SYSTEM DEPLOYMENT")
    print("=" * 60)

    create_backup()
    clean_old_files()
    create_structure()
    print_summary()

if __name__ == "__main__":
    main()