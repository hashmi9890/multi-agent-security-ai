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