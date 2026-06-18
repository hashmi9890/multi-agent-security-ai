from src.core.orchestrator import SecurityOrchestrator

def test_orchestrator_init():
    orch = SecurityOrchestrator()
    assert orch is not None

def test_threat_agent():
    orch = SecurityOrchestrator()  
    result = orch.process("Detected ransomware attack")
    assert result["status"] == "success"
    assert result["agent"] == "threat"