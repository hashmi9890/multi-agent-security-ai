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