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
        return "\n".join([f"{m.role}: {m.content}" for m in self.history[-self.max_history:]])

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