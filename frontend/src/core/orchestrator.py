from typing import Dict
from datetime import datetime
import logging
from src.core.memory import ConversationMemory
from src.agents.master_agent import MasterAgent

logger = logging.getLogger(__name__)

class SecurityOrchestrator:
    def __init__(self):
        self.memory = ConversationMemory()
        self.master_agent = MasterAgent()
        logger.info("[ORCH] Initialized with MasterAgent")

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
        return {
            "status": "success",
            "agent": res.get("agent", "MasterAgent"),
            "output": res.get("output", ""),
            "metadata": res.get("metadata", {}),
            "latency_ms": res.get("latency_ms", 0)
        }

    def get_system_status(self) -> Dict:
        res = self.master_agent._status()
        meta = res.get("metadata", {})
        status = meta.get("status", {})
        return {
            "master_agent": status.get("master", {"name": "MasterAgent"}),
            "agents_loaded": status.get("agents", []),
            "memory_stats": self.memory.get_stats()
        }

    def reset_memory(self, user_id=None):
        if user_id:
            self.memory.clear_user(user_id)
        else:
            self.memory.clear_all()
