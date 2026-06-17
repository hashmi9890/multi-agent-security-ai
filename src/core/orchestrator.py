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