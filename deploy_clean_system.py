#!/usr/bin/env python3
import os, shutil, textwrap, json
from pathlib import Path
from datetime import datetime

BACKUP = Path(f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
STRUCTURE = {
    "src": {
        "__init__.py": "",  
        "agents": {
            "__init__.py": "from src.agents.master_agent import MasterAgent\n__all__ = ['MasterAgent']",
            "base_agent.py": """
from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime
class BaseAgent(ABC):
    def __init__(self, name: str, agent_type: str):
        self.name = name
        self.agent_type = agent_type
        self.created_at = datetime.now().isoformat()
    @abstractmethod
    def execute(self, prompt: Dict[str, str], metadata: Dict = None) -> Dict[str, Any]:
        pass
    def _build_response(self, output: str, metadata: Dict = None) -> Dict:
        return {"output": output, "agent": self.name, "metadata": metadata or {}}
    def get_info(self) -> Dict:
        return {"name": self.name, "type": self.agent_type}
""",
            "master_agent.py": """
from typing import Dict, List, Any
import logging
from datetime import datetime
from src.agents.base_agent import BaseAgent
from src.agents.threat_analyzer import ThreatAnalyzerAgent
from src.agents.vulnerability_scanner import VulnerabilityScannerAgent
from src.agents.log_parser import LogParserAgent
from src.agents.incident_responder import IncidentResponderAgent
from src.agents.job_finder import JobFinderAgent
from src.core.router import IntentRouter
from src.core.prompt_engine import PromptEngine
logger = logging.getLogger(__name__)
class MasterAgent(BaseAgent):
    def __init__(self):
        super().__init__("MasterAgent", "master")
        self.router = IntentRouter()
        self.prompt_engine = PromptEngine()
        self.sub_agents: Dict[str, BaseAgent] = {}
        self.agent_registry: Dict[str, type] = {}
        self._register_agents()
        self._init_agents()
        logger.info("[MASTER] Initialized")
    def _register_agents(self):
        self.agent_registry = {"threat": ThreatAnalyzerAgent, "vulnerability": VulnerabilityScannerAgent, "log": LogParserAgent, "incident": IncidentResponderAgent, "job": JobFinderAgent}
    def _init_agents(self):
        for t, c in self.agent_registry.items():
            try:
                self.sub_agents[t] = c()
                logger.info(f"[MASTER] Loaded: {t}")
            except Exception as e:
                logger.error(f"[MASTER] Failed {t}: {e}")
    def execute(self, prompt: Dict[str, str], metadata: Dict = None) -> Dict[str, Any]:
        start = datetime.now()
        user_input = prompt.get("user", "")
        logger.info(f"[MASTER] Input: {user_input[:50]}")
        if "[TEST_ALL_AGENTS]" in user_input or "[BROADCAST]" in user_input:
            result = self._broadcast(prompt, metadata)
        elif "[STATUS]" in user_input:
            result = self._status()
        elif "[PROACTIVE_JOB_SCAN]" in user_input:
            result = self._job_scan(prompt, metadata)
        else:
            result = self._route(prompt, metadata)
        result["latency_ms"] = round((datetime.now() - start).total_seconds() * 1000, 2)
        result["agent"] = self.name
        result["timestamp"] = datetime.now().isoformat()
        return result
    def _route(self, prompt, metadata):
        user_input = prompt.get("user", "")
        routing = self.router.route(user_input)
        intent, conf = routing["intent"], routing["confidence"]
        agent = self.sub_agents.get(intent)
        if not agent:
            return self._resp("[MASTER] General query. No agent matched.", {"mode": "fallback", "routing": routing, **(metadata or {})})
        logger.info(f"[MASTER] Delegating to {intent}")
        try:
            res = agent.execute(prompt, metadata)
            return self._resp(res.get("output", ""), {"mode": "single", "delegated_to": intent, "agent_name": agent.name, "confidence": f"{conf:.0%}", **(metadata or {})})
        except Exception as e:
            return self._resp(f"[ERROR] {e}", {"mode": "error", "error": str(e)})
    def _broadcast(self, prompt, metadata):
        logger.info("[MASTER] Broadcasting")
        execs, combined = [], "MULTI-AGENT REPORT\\n" + "="*60 + "\\n\\n"
        for t, a in self.sub_agents.items():
            try:
                r = a.execute(prompt, metadata)
                execs.append({"agent": a.name, "success": True})
                combined += f"[{a.name}]\\n{r.get('output', '')}\\n\\n"
            except Exception as e:
                execs.append({"agent": a.name, "success": False})
        combined += "="*60 + f"\\nSUMMARY: {sum(1 for e in execs if e['success'])}/{len(execs)} OK\\n"
        return self._resp(combined, {"mode": "broadcast", "executions": execs, **(metadata or {})})
    def _job_scan(self, prompt, metadata):
        agent = self.sub_agents.get("job")
        if not agent:
            return self._resp("[ERROR] JobFinder unavailable", {"mode": "error"})
        res = agent.execute(prompt, metadata)
        return self._resp(res.get("output", ""), {"mode": "job_scan", **(metadata or {})})
    def _status(self):
        s = {"agents": list(self.sub_agents.keys()), "count": len(self.sub_agents)}
        out = f"MASTER STATUS\\nAgents: {s['count']}\\n" + "\\n".join(f"  - {a}" for a in s["agents"])
        return self._resp(out, {"mode": "status", "status": s})
    def _resp(self, out, meta):
        return {"output": out, "agent": self.name, "metadata": meta}
    def list_agents(self):
        return list(self.sub_agents.keys())
""",
            "threat_analyzer.py": "from src.agents.base_agent import BaseAgent\nclass ThreatAnalyzerAgent(BaseAgent):\n    def __init__(self): super().__init__('ThreatAnalyzer', 'threat')\n    def execute(self, p, m=None): return self._build_response('[THREAT] Scan complete. No active threats.', m)",
            "vulnerability_scanner.py": "from src.agents.base_agent import BaseAgent\nclass VulnerabilityScannerAgent(BaseAgent):\n    def __init__(self): super().__init__('VulnScanner', 'vulnerability')\n    def execute(self, p, m=None): return self._build_response('[VULN] Scan complete. System secure.', m)",
            "log_parser.py": "from src.agents.base_agent import BaseAgent\nclass LogParserAgent(BaseAgent):\n    def __init__(self): super().__init__('LogParser', 'log')\n    def execute(self, p, m=None): return self._build_response('[LOG] Analysis complete. No anomalies.', m)",
            "incident_responder.py": "from src.agents.base_agent import BaseAgent\nclass IncidentResponderAgent(BaseAgent):\n    def __init__(self): super().__init__('IncidentResponder', 'incident')\n    def execute(self, p, m=None): return self._build_response('[INCIDENT] Playbook ready.', m)",
            "job_finder.py": """
from src.agents.base_agent import BaseAgent
from typing import Dict, Any, List
class JobFinderAgent(BaseAgent):
    def __init__(self):
        super().__init__("JobFinder", "job")
        self.kws = ["python", "ai", "security", "remote"]
    def execute(self, p, m=None):
        jobs = self._scan(p.get("user", ""))
        if not jobs:
            return self._build_response("[JOB] No matching jobs found.", {"jobs": [], **(m or {})})
        out = f"JOBS FOUND: {len(jobs)}\\n\\n"
        for j in jobs:
            out += f"- {j['title']} @ {j['company']}\\n  {j['salary']} | {j['url']}\\n\\n"
        return self._build_response(out, {"jobs": jobs, **(m or {})})
    def _scan(self, q):
        mocks = [{"title": "AI Security Eng", "company": "CyberTech", "salary": "$120K", "url": "http://ex.com/1"},
                 {"title": "Python Dev", "company": "RemoteInc", "salary": "$80/hr", "url": "http://ex.com/2"}]
        return [j for j in mocks if any(k in q.lower() for k in self.kws) or "[PROACTIVE]" in q]
    def get_alert_message(self, jobs):
        if not jobs: return "[JOB] No new jobs."
        msg = f"JOB ALERT: {len(jobs)} new\\n\\n"
        for j in jobs[:3]:
            msg += f"- {j['title']} @ {j['company']} ({j['salary']})\\n"
        return msg
"""
        },
        "core": {
            "__init__.py": "",
            "orchestrator.py": """
from typing import Dict
from datetime import datetime
import logging
from src.core.memory import ConversationMemory
from src.agents.master_agent import MasterAgent
logger = logging.getLogger(__name__)
class SecurityOrchestrator:
    def __init__(self, config=None):        
        self.memory = ConversationMemory()
        self.master_agent = MasterAgent()
        logger.info("[ORCH] Initialized")
    def process(self, user_input: str, user_id="default") -> Dict:
        start = datetime.now()
        ctx = self.memory.get_context(user_id, 10)
        prompt = {"system": "Multi-Agent AI", "user": user_input, "context": ctx}
        try:
            res = self.master_agent.execute(prompt, {"user_id": user_id})
        except Exception as e:
            return {"status": "error", "message": str(e)}
        self.memory.add(user_id, "user", user_input)
        self.memory.add(user_id, "assistant", res.get("output", ""))
        meta = res.get("metadata", {})
        return {"status": "success", "agent": res.get("agent"), "mode": meta.get("mode", "single"),
                "output": res.get("output", ""), "metadata": meta,
                "latency_ms": res.get("latency_ms", round((datetime.now()-start).total_seconds()*1000, 2))}
    def get_system_status(self):
        res = self.master_agent._status()
        return {"master_agent": {"name": self.master_agent.name},
                "agents_loaded": res["metadata"]["status"]["agents"],
                "memory_stats": self.memory.get_stats()}
    def reset_memory(self, uid=None):
        if uid: self.memory.clear_user(uid)
        else: self.memory.clear_all()
""",
            "memory.py": """
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
    def __init__(self, persist_dir="data/memory", max_history=50):
        self.dir = Path(persist_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.max = max_history
        self.sessions: Dict[str, List[Message]] = {}
        self._load()
    def add(self, uid, role, content):
        if uid not in self.sessions: self.sessions[uid] = []
        self.sessions[uid].append(Message(role, content))
        if len(self.sessions[uid]) > self.max:
            self.sessions[uid] = self.sessions[uid][-self.max:]
        self._save(uid)
    def get_context(self, uid, limit=10):
        msgs = self.sessions.get(uid, [])
        return "\\n".join(f"{m.role}: {m.content}" for m in msgs[-limit:])
    def _save(self, uid):
        with open(self.dir / f"{uid}.json", "w") as f:
            json.dump({"messages": [asdict(m) for m in self.sessions[uid]]}, f)
    def _load(self):
        for f in self.dir.glob("*.json"):
            try:
                with open(f) as fp:
                    d = json.load(fp)
                    self.sessions[f.stem] = [Message(**m) for m in d.get("messages", [])]
            except: pass
    def get_stats(self):
        return {"total_messages": sum(len(m) for m in self.sessions.values())}
    def clear_user(self, uid):
        self.sessions.pop(uid, None)
        (self.dir / f"{uid}.json").unlink(missing_ok=True)
    def clear_all(self):
        self.sessions.clear()
        for f in self.dir.glob("*.json"): f.unlink()
""",
            "router.py": """
class IntentRouter:
    KWS = {"threat": ["threat", "malware"], "vulnerability": ["cve", "vuln"], "log": ["log", "siem"], "incident": ["breach", "incident"], "job": ["job", "hire"]}
    @staticmethod
    def route(text):
        t = text.lower()
        best, score = "general", 0
        for i, ks in IntentRouter.KWS.items():
            s = sum(1 for k in ks if k in t)
            if s > score: best, score = i, s
        return {"intent": best, "confidence": min(score/2, 1.0)}
""",
            "prompt_engine.py": """
class PromptEngine:
    @staticmethod
    def build(intent, inp, ctx=""):
        return {"system": f"You are {intent} agent.", "user": f"Context: {ctx}\\n\\nInput: {inp}"}
"""
        },
        "integrations": {
            "__init__.py": "",
            "twilio_client.py": """
import os
from twilio.rest import Client
import logging
logger = logging.getLogger(__name__)
class TwilioClient:
    def __init__(self):
        self.client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        self.wa = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
        self.voice = os.getenv("TWILIO_VOICE_NUMBER")
        logger.info("[TWILIO] Init")
    def send_whatsapp(self, to, msg):
        try:
            if not to.startswith("whatsapp:"): to = f"whatsapp:{to}"
            self.client.messages.create(body=msg, from_=self.wa, to=to)
            return True
        except Exception as e:
            logger.error(f"[TWILIO] WA fail: {e}")
            return False
    def make_call(self, to, msg):
        try:
            self.client.calls.create(twiml=f"<Response><Say>{msg}</Say></Response>", from_=self.voice, to=to)
            return True
        except Exception as e:
            logger.error(f"[TWILIO] Call fail: {e}")
            return False
""",
            "whatsapp_bridge.py": """
import os, sys
from pathlib import Path
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import logging
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
load_dotenv()
from src.agents.master_agent import MasterAgent
from src.core.memory import ConversationMemory
from src.integrations.twilio_client import TwilioClient
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
app = Flask(__name__)
master = MasterAgent()
mem = ConversationMemory()
twilio = TwilioClient()
sched = BackgroundScheduler()
@app.route("/whatsapp", methods=["POST"])
def webhook():
    try:
        inp = request.values.get("Body", "").strip()
        uid = request.values.get("From", "u").replace("whatsapp:", "")
        logger.info(f"[WA] {uid}: {inp[:40]}")
        prompt = {"user": inp, "context": mem.get_context(uid, 5)}
        res = master.execute(prompt, {"user_id": uid})
        out = res.get("output", "[ERROR] No response")
        mem.add(uid, "user", inp)
        mem.add(uid, "assistant", out)
        resp = MessagingResponse()
        for chunk in [out[i:i+1500] for i in range(0, len(out), 1500)]:
            resp.message(chunk)
        return str(resp), 200
    except Exception as e:
        logger.error(f"[WA] Err: {e}")
        return str(MessagingResponse().message(f"[ERROR] {e}")), 500
def job_task():
    logger.info("[SCHED] Job scan")
    try:
        res = master.execute({"user": "[PROACTIVE_JOB_SCAN]"}, {"src": "sched"})
        jobs = res.get("metadata", {}).get("jobs", [])
        if jobs:
            alert = master.sub_agents.get("job").get_alert_message(jobs)
            twilio.send_whatsapp(os.getenv("ADMIN_WHATSAPP"), alert)
    except Exception as e:
        logger.error(f"[SCHED] Job err: {e}")
def rem_task():
    logger.info("[SCHED] Reminder")
    twilio.send_whatsapp(os.getenv("ADMIN_WHATSAPP"), "DAILY REMINDER: Check logs & patches. Reply [STATUS].")
sched.add_job(job_task, "interval", minutes=30)
sched.add_job(rem_task, "cron", hour=9)
sched.start()
logger.info("[SCHED] Started")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("WHATSAPP_PORT", 5000)))
"""
        },
        "ui": {
            "__init__.py": "",
            "streamlit_app.py": """
import streamlit as st
import json, sys
from datetime import datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.core.orchestrator import SecurityOrchestrator
st.set_page_config(page_title="CYBERPUNK SECURITY AI", layout="wide")
CSS = '''
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Share+Tech+Mono&display=swap');
.stApp { background: linear-gradient(135deg, #0a0a0f, #1a0a2e); font-family: 'Share Tech Mono'; }
h1 { font-family: 'Orbitron'; color: #00f3ff; text-shadow: 0 0 10px #00f3ff; }
.stChatMessage { background: rgba(0,243,255,0.05); border-left: 3px solid #00f3ff; }
.stTextInput input { background: #000; border: 2px solid #00f3ff; color: #00f3ff; }
.stButton button { background: transparent; border: 2px solid #00f3ff; color: #00f3ff; }
.stButton button:hover { background: #00f3ff; color: #000; }
</style>
'''
st.markdown(CSS, unsafe_allow_html=True)
@st.cache_resource
def get_orch(): return SecurityOrchestrator()
orch = get_orch()
if "msgs" not in st.session_state: st.session_state.msgs = []
if "uid" not in st.session_state: st.session_state.uid = "u_" + datetime.now().strftime("%H%M%S")
with st.sidebar:
    st.markdown("## SYSTEM")
    s = orch.get_system_status()
    st.metric("MASTER", s["master_agent"]["name"])
    st.metric("AGENTS", len(s["agents_loaded"]))
    if st.button("PURGE MEM"):
        orch.reset_memory(st.session_state.uid)
        st.session_state.msgs = []
        st.rerun()
st.markdown("<h1>CYBERPUNK SECURITY AI</h1>", unsafe_allow_html=True)
for m in st.session_state.msgs:
    with st.chat_message(m["role"]):
        st.write(m["content"])
        if "meta" in m:
            with st.expander("META"): st.json(m["meta"])
if p := st.chat_input("COMMAND"):
    st.session_state.msgs.append({"role": "user", "content": p})
    with st.chat_message("user"): st.write(p)
    with st.chat_message("assistant"):
        with st.spinner("PROC..."):
            r = orch.process(p, st.session_state.uid)
        if r["status"] == "success":
            st.write(r["output"])
            st.session_state.msgs.append({"role": "assistant", "content": r["output"], "meta": r.get("metadata", {})})
        else:
            st.error(r["message"])
"""
        }
    },
    "data": {"memory": {}, "logs": {}},
    "requirements.txt": "streamlit>=1.28.0\nflask>=3.0.0\ntwilio>=8.0.0\napscheduler>=3.10.0\npython-dotenv>=1.0.0\nopenai>=1.0.0\npydantic>=2.0.0\nloguru>=0.7.0",
    ".env.example": "LLM_API_KEY=\nTWILIO_ACCOUNT_SID=\nTWILIO_AUTH_TOKEN=\nTWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886\nADMIN_WHATSAPP=whatsapp:+923000000000\nWHATSAPP_PORT=5000",
    ".gitignore": "__pycache__/\n*.pyc\n.venv/\n.env\ndata/memory/*.json\n*.log\n.streamlit/\nbackup_*/",
    "README.md": "# CLEAN MULTI-AGENT SECURITY AI\n\nNo emojis, Windows ready.\n\n## Run\npip install -r requirements.txt\ncp .env.example .env\npython run_system.py",
    "run_system.py": """
import subprocess, sys, signal, os
def run():
    print("STARTING SYSTEM...")
    print("UI: http://localhost:8501")
    print("WA: http://localhost:5000")
    b = subprocess.Popen([sys.executable, "-m", "src.integrations.whatsapp_bridge"])
    u = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "src/ui/streamlit_app.py"])
    def stop(s, f):
        print("\\nSTOPPING...")
        b.terminate()
        u.terminate()
        sys.exit(0)
    signal.signal(signal.SIGINT, stop)
    try:
        b.wait()
        u.wait()
    except KeyboardInterrupt:
        stop(None, None)
if __name__ == "__main__":
    run()
"""
}

def backup():
    print(f"[DEPLOY] Backup: {BACKUP}")
    Path(BACKUP).mkdir(exist_ok=True)
    for i in Path(".").iterdir():
        if i.name in [BACKUP, "deploy_clean_system.py", ".git"]: continue
        if i.is_file(): shutil.copy2(i, BACKUP/i.name)
        elif i.is_dir(): shutil.copytree(i, BACKUP/i.name, dirs_exist_ok=True)

def create():
    print("[DEPLOY] Creating files...")
    def rec(base, struct):
        base.mkdir(parents=True, exist_ok=True)
        for n, c in struct.items():
            p = base / n
            if isinstance(c, dict):
                rec(p, c)
            else:
                with open(p, "w", encoding="utf-8") as f:
                    f.write(c.strip() if isinstance(c, str) else "")
                print(f"  + {p}")
    rec(Path("."), STRUCTURE)

if __name__ == "__main__":
    backup()
    create()
    print("[DEPLOY] DONE. Run: pip install -r requirements.txt && cp .env.example .env && python run_system.py")
