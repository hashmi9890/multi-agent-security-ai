from src.agents.threat_analyzer import ThreatAnalyzerAgent
from src.agents.vulnerability_scanner import VulnerabilityScannerAgent
from src.agents.log_parser import LogParserAgent
from src.agents.incident_responder import IncidentResponderAgent

AGENT_REGISTRY = {
    "threat": ThreatAnalyzerAgent,
    "vulnerability": VulnerabilityScannerAgent,
    "log": LogParserAgent,
    "incident": IncidentResponderAgent
}

def get_agent(agent_type: str):
    agent_class = AGENT_REGISTRY.get(agent_type)
    if not agent_class:
        raise ValueError(f"Unknown agent type: {agent_type}")
    return agent_class()

__all__ = ["get_agent", "AGENT_REGISTRY"]