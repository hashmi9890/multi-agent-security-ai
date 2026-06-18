from src.agents.worker_agents import ResearchAgent, CodeAgent, DataAnalysisAgent

from src.agents.head_agent import HeadAgent
from src.agents.security_agents import InputSecurityAgent, OutputSecurityAgent

from src.persistent_memory import PersistentMemory
from src.vector_memory import VectorMemory


memory = PersistentMemory()
vector_memory = VectorMemory()


def run_research_workflow(user_input: str) -> str:

    print("🛡️ Step 1: Running Input Security Check...")

    input_guard = InputSecurityAgent()
    is_safe, msg = input_guard.check(user_input)
    if not is_safe:
        return f"BLOCKED: {msg}"

    memory.add("user", user_input)
    vector_memory.add("user", user_input)

    print("🧠 Step 2: Semantic Context Retrieval...")

    semantic_context = vector_memory.search(user_input, k=4)

    print("🧠 Step 3: Head Agent Planning & Routing...")

    head = HeadAgent("HeadAgent")

    full_context = f"""
Recent Memory:
{memory.get_context(limit=5)}

Semantic Memory:
{semantic_context}
"""

    plan = head.create_plan(full_context)
    route = head.route_task(full_context)

    worker_type = route.get("worker_type")
    task = route.get("task_description", user_input)

    context = f"""
Conversation Context:
{full_context}

Execution Plan:
{plan}

Current Task:
{task}
"""

    print(f"⚙️ Step 4: Executing task with '{worker_type.upper()}' Agent...")

    if worker_type == "code":
        worker = CodeAgent()
    elif worker_type == "data_analysis":
        worker = DataAnalysisAgent()
    else:
        worker = ResearchAgent()

    output = worker.run(context)

    print("🛡️ Step 5: Running Output Security Check...")

    output_guard = OutputSecurityAgent()
    safe, msg = output_guard.check(output)
    if not safe:
        return f"OUTPUT BLOCKED: {msg}"

    memory.add("assistant", output)
    vector_memory.add("assistant", output)

    print("✅ Workflow Completed Successfully!")

    return output 

    from src.agents.worker_agents import ResearchAgent, CodeAgent, DataAnalysisAgent, SQLSolverAgent


    if worker_type == "code":
        worker = CodeAgent()
    elif worker_type == "data_analysis":
        worker = DataAnalysisAgent()
    elif worker_type == "sql_software":
        worker = SQLSolverAgent()
    else:
        worker = ResearchAgent()