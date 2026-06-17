"""Head agent orchestration logic."""


SQL_SOFTWARE_KEYWORDS = [
    "sql", "query", "select *", "join", "database", "schema",
    "stored procedure", "index", "primary key", "foreign key",
    "deadlock", "null pointer", "segmentation fault", "stack overflow",
    "module not found", "dependency error", "pip install", "npm install",
    "permission denied", "connection refused", "500 error", "404",
    "server error", "installation error", "environment error",
    "indentation error", "syntax error", "traceback",
]

CODE_KEYWORDS = [
    "code", "function", "bug", "error", "debug", "exception",
    "script", "python", "javascript", "java", "c++",
    "compile", "class ", "def ", "import ", "variable",
    "algorithm", "refactor", "fix this", "write a program",
]

DATA_KEYWORDS = [
    "csv", "dataset", "data analysis", "average", "mean", "median",
    "statistics", "stats", "trend", "correlation", "spreadsheet",
    "rows", "columns", "table", "sum of", "total sales", "analyze this data",
]


class HeadAgent:
    def __init__(self, name: str) -> None:
        self.name = name

    def coordinate(self) -> None:
        print(f"{self.name} coordinating workers...")

    def create_plan(self, user_input: str) -> dict:
        """Create a simple plan for handling the user's request."""
        return {
            "original_input": user_input,
            "steps": ["analyze_request", "route_to_worker", "execute", "return_result"],
        }

    def route_task(self, user_input: str) -> dict:
        """Decide which worker should handle this task based on keywords."""
        lowered = user_input.lower()

        if any(keyword in lowered for keyword in SQL_SOFTWARE_KEYWORDS):
            worker_type = "sql_software"
        elif any(keyword in lowered for keyword in DATA_KEYWORDS):
            worker_type = "data_analysis"
        elif any(keyword in lowered for keyword in CODE_KEYWORDS):
            worker_type = "code"
        else:
            worker_type = "research"

        return {
            "worker_type": worker_type,
            "task_description": user_input,
        }