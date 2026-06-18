import logging
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MasterAgent")


class MasterAgent:
    """
    Master Agent responsible for receiving security tasks, orchestrating specialized 
    sub-agents (like BashTerminalAgent, WebScanner, etc.), and aggregating the final report.
    """

    def __init__(self, name: str = "Master Security Orchestrator", agents: Optional[List[Any]] = None):
        self.name = name
        self.agents = agents or []

    def register_agent(self, agent: Any) -> None:
        """Registers a specialized security sub-agent."""
        self.agents.append(agent)
        logger.info(f"Registered sub-agent: {agent.name}")

    def run(self, task: str, target: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes the security task across all relevant registered sub-agents
        and combines their outputs into a comprehensive security summary.
        """
        logger.info(f"[{self.name}] Starting task: '{task}' on target: '{target or 'None'}'")
        
        results: List[Dict[str, Any]] = []
        combined_output = f"### Security Orchestration Report for Task: {task}\n"
        if target:
            combined_output += f"**Target:** `{target}`\n"
        combined_output += "=" * 50 + "\n\n"

        # Delegate task to sub-agents
        for agent in self.agents:
            try:
                logger.info(f"[{self.name}] Delegating to -> {agent.name}")
                # Assume each sub-agent has a run() method returning a dict
                r = agent.run(task=task, target=target)
                results.append(r)

                # Corrected line 75: using single quotes inside r.get('output', '')
                combined_output += f"#### [{agent.name}]\n{r.get('output', 'No output generated.')}\n\n"
                
            except Exception as e:
                logger.error(f"[{self.name}] Error running {agent.name}: {str(e)}")
                combined_output += f"#### [{agent.name}] - FAILED\nError: {str(e)}\n\n"

        combined_output += "=" * 50 + "\n"
        
        return {
            "status": "completed",
            "task": task,
            "target": target,
            "output": combined_output,
            "sub_agent_results": results
        }