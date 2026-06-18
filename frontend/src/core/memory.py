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
        return "\n".join([f"{m.role}: {m.content}" for m in recent])

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