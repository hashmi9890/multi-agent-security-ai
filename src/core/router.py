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