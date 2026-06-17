"""Orchestrator: routes user input through security + the right worker agent."""

from src.agents.head_agent import HeadAgent
from src.agents.worker_agents import ResearchAgent, CodeAgent, DataAnalysisAgent, SQLSolverAgent
from src.agents.security_agents import InputSecurityAgent, OutputSecurityAgent

WORKER_LABELS = {
    "research": "🔍 Research Agent",
    "code": "💻 Code Agent",
    "data_analysis": "📊 Data Analysis Agent",
    "sql_software": "🛠️ SQL/Software Solver Agent",
}


class Orchestrator:
    def __init__(self):
        self.head_agent = HeadAgent(name="HeadAgent")
        self.input_guard = InputSecurityAgent()
        self.output_guard = OutputSecurityAgent()
        self.workers = {
            "research": ResearchAgent(),
            "code": CodeAgent(),
            "data_analysis": DataAnalysisAgent(),
            "sql_software": SQLSolverAgent(),
        }

    def handle(self, user_input: str) -> dict:
        # 1) Input security check
        is_safe, reason = self.input_guard.check(user_input)
        if not is_safe:
            return {
                "status": "blocked_input",
                "agent_label": "🛑 Input Security Agent",
                "content": f"Request blocked by security layer.\n\n**Reason:** {reason}",
                "usage": None,
            }

        # 2) Route via HeadAgent
        plan = self.head_agent.route_task(user_input)
        worker_type = plan["worker_type"]
        worker = self.workers[worker_type]
        agent_label = WORKER_LABELS.get(worker_type, worker_type)

        # 3) Run the chosen worker agent
        try:
            worker_result = worker.run(plan["task_description"])
            raw_response = worker_result["content"]
            usage = worker_result["usage"]
        except Exception as e:
            return {
                "status": "error",
                "agent_label": agent_label,
                "content": f"Agent execution failed: {e}",
                "usage": None,
            }

        # 4) Output security check
        is_output_safe, out_reason = self.output_guard.check(raw_response)
        if not is_output_safe:
            return {
                "status": "blocked_output",
                "agent_label": "🛑 Output Security Agent",
                "content": f"Response blocked by security layer.\n\n**Reason:** {out_reason}",
                "usage": usage,
            }

        return {
            "status": "ok",
            "agent_label": agent_label,
            "content": raw_response,
            "usage": usage,
        }