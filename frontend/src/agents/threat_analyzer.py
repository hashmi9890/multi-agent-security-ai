from src.agents.base_agent import BaseAgent
from typing import Dict, Any
import re

class ThreatAnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__("ThreatAnalyzer", "threat")
        self.threat_db = {
            "ransomware": {"severity": "CRITICAL", "type": "Malware", "mitigation": "Isolate systems, restore from backup"},
            "phishing": {"severity": "HIGH", "type": "Social Engineering", "mitigation": "User training, email filtering"},
            "sql_injection": {"severity": "CRITICAL", "type": "Web Attack", "mitigation": "Input validation, parameterized queries"},
            "xss": {"severity": "HIGH", "type": "Web Attack", "mitigation": "Output encoding, CSP headers"}
        }

    def execute(self, prompt: Dict[str, str], metadata: Dict = None) -> Dict[str, Any]:
        user_input = prompt.get("user", "")
        findings = []
        detected_threats = []

        for threat, info in self.threat_db.items():
            if threat in user_input.lower():
                detected_threats.append(threat)
                findings.append({
                    "threat": threat,
                    "severity": info["severity"],
                    "type": info["type"],
                    "mitigation": info["mitigation"]
                })

        if not detected_threats:
            output = "🔍 No known threat indicators detected. Continue monitoring."
        else:
            output = f"⚠️ THREAT DETECTED: {', '.join(detected_threats)}\n\n"
            for f in findings:
                output += f"📌 {f['threat'].upper()}\n"
                output += f"   Severity: {f['severity']}\n"
                output += f"   Type: {f['type']}\n"
                output += f"   Mitigation: {f['mitigation']}\n\n"
            output += "🚨 Recommended: Isolate affected systems and initiate incident response."

        return self._build_response(output, {
            "detected_threats": detected_threats,
            "count": len(detected_threats),
            **(metadata or {})
        })