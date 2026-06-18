from src.agents.base_agent import BaseAgent
from typing import Dict, Any
import re

class LogParserAgent(BaseAgent):
    def __init__(self):
        super().__init__("LogParser", "log")
        self.patterns = {
            "failed_login": r"failed.?login|authentication.?fail",
            "privilege_escalation": r"privilege.?escalat|sudo|admin.?access",
            "data_exfil": r"exfil|large.?transfer|unusual.?outbound"
        }

    def execute(self, prompt: Dict[str, str], metadata: Dict = None) -> Dict[str, Any]:
        user_input = prompt.get("user", "")
        alerts = []

        for alert_type, pattern in self.patterns.items():
            if re.search(pattern, user_input, re.IGNORECASE):
                alerts.append(alert_type)

        if not alerts:
            output = "📊 Log analysis complete. No anomalies detected."
        else:
            output = "🚨 ANOMALIES DETECTED IN LOGS:\n\n"
            for alert in alerts:
                output += f"⚠️ {alert.replace('_', ' ').title()}\n"
            output += "\n🔍 Recommended: Investigate flagged events immediately."

        return self._build_response(output, {
            "alerts": alerts,
            "alert_count": len(alerts),
            **(metadata or {})
        })