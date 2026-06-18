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
            user_template="Context:\n{context}\n\nThreat Query: {input}\n\nAnalysis:"
        ),
        "vulnerability": SecurityPrompt(
            system="You are a Vulnerability Assessment Agent. Identify security weaknesses, CVEs, and misconfigurations. Provide risk scores and remediation guidance.",
            user_template="Context:\n{context}\n\nVulnerability Check: {input}\n\nAssessment:"
        ),
        "log": SecurityPrompt(
            system="You are a Log Analysis Agent. Parse security logs, detect anomalies, and correlate events. Highlight suspicious activities.",
            user_template="Context:\n{context}\n\nLog Data: {input}\n\nFindings:"
        ),
        "incident": SecurityPrompt(
            system="You are an Incident Response Agent. Provide actionable steps for security incidents. Follow IR playbook: Detect, Analyze, Contain, Eradicate, Recover.",
            user_template="Context:\n{context}\n\nIncident: {input}\n\nResponse Plan:"
        ),
        "general": SecurityPrompt(
            system="You are a Security Assistant. Provide accurate, concise security information. When unsure, recommend consulting specialized agents.",
            user_template="Context:\n{context}\n\nQuery: {input}\n\nResponse:"
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