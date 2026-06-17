# 🛡️ Multi-Agent Security AI System

Advanced security analysis platform with specialized AI agents for threat detection, vulnerability assessment, log analysis, and incident response.

## 🚀 Features

- **Multi-Agent Architecture**: Specialized agents for different security domains
- **Intelligent Routing**: Automatic intent detection and agent selection
- **Persistent Memory**: Conversation history with JSON persistence
- **Streamlit UI**: Interactive web interface with debug panels
- **Production Ready**: Logging, error handling, type hints

## 📁 Structure

```
multi_agent_security_ai/
├── src/
│   ├── core/          # Orchestrator, memory, router, prompts
│   ├── agents/        # Security agents (threat, vuln, log, incident)
│   ├── ui/           # Streamlit interface
│   └── utils/        # Helpers, config
├── tests/            # Test suite
├── data/             # Memory persistence, logs
└── requirements.txt
```

## 🛠️ Setup

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 4. Run application
streamlit run src/ui/streamlit_app.py
```

## 🤖 Agents

| Agent | Purpose |
|-------|---------|
| ThreatAnalyzer | Detect malware, attacks, IOCs |
| VulnScanner | Identify CVEs, weaknesses |
| LogParser | Parse logs, detect anomalies |
| IncidentResponder | IR playbook, response steps |

## 📝 Usage Examples

```
"Analyze this log for suspicious activity: [paste log]"
"Check for CVE-2024-0001 vulnerability"
"Detected ransomware attack, what should I do?"
"Failed login attempts from IP 192.168.1.100"
```

## 🔒 Security Note

This system is for defensive security analysis. Ensure proper authorization before scanning systems.

## 📄 License

MIT License