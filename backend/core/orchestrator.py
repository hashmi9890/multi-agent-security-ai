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
            "coder": "```python\n# Generated Code\ndef solution():\n    return 'Success!'\n```",
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