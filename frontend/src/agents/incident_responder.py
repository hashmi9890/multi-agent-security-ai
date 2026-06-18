from src.agents.base_agent import BaseAgent
from typing import Dict, Any

class IncidentResponderAgent(BaseAgent):
    def __init__(self):
        super().__init__("IncidentResponder", "incident")
        self.playbook = {
            "containment": ["Isolate affected systems", "Block malicious IPs", "Disable compromised accounts"],
            "eradication": ["Remove malware", "Patch vulnerabilities", "Reset credentials"],
            "recovery": ["Restore from clean backup", "Verify system integrity", "Monitor for recurrence"]
        }

    def execute(self, prompt: Dict[str, str], metadata: Dict = None) -> Dict[str, Any]:
        user_input = prompt.get("user", "")
        output = "📋 INCIDENT RESPONSE PLAYBOOK\n\n"

        for phase, steps in self.playbook.items():
            output += f"🔹 {phase.upper()}\n"
            for i, step in enumerate(steps, 1):
                output += f"   {i}. {step}\n"
            output += "\n"

        output += "📞 Escalation: Contact SOC team if severity is HIGH or CRITICAL."

        return self._build_response(output, {
            "phases": list(self.playbook.keys()),
            **(metadata or {})
        })