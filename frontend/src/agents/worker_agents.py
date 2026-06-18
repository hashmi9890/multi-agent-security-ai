from src.config import get_llm
from src.agents.utils import extract_usage


# =========================
# Research Agent
# =========================

class ResearchAgent:
    def __init__(self):
        self.llm = get_llm(temperature=0.5)

    def run(self, task_description: str) -> dict:
        prompt = (
            "You are a professional research analyst.\n\n"
            f"Task:\n{task_description}\n\n"
            "Provide:\n"
            "- 3-5 bullet points\n"
            "- Executive Summary\n"
            "Be concise and factual."
        )
        resp = self.llm.invoke(prompt)
        return {
            "content": resp.content.strip(),
            "usage": extract_usage(resp),
        }


# =========================
# Code Agent
# =========================

class CodeAgent:
    def __init__(self):
        self.llm = get_llm(temperature=0.2)

    def run(self, task_description: str) -> dict:
        prompt = (
            "You are a senior software engineer.\n\n"
            f"Task:\n{task_description}\n\n"
            "Rules:\n"
            "- Return clean working production-ready code.\n"
            "- Wrap code inside proper fenced code blocks.\n"
            "- Keep explanation short and technical.\n"
        )
        resp = self.llm.invoke(prompt)
        return {
            "content": resp.content.strip(),
            "usage": extract_usage(resp),
        }


# =========================
# Data Analysis Agent
# =========================

class DataAnalysisAgent:
    def __init__(self):
        self.llm = get_llm(temperature=0.1)

    def run(self, task_description: str) -> dict:
        prompt = (
            "You are a senior business data analyst.\n\n"
            f"Task:\n{task_description}\n\n"
            "Structure your response using:\n"
            "## Key Metrics\n"
            "## Insights\n"
            "## Business Impact\n"
            "## Recommendations\n"
            "Be concise and do not fabricate data."
        )
        resp = self.llm.invoke(prompt)
        return {
            "content": resp.content.strip(),
            "usage": extract_usage(resp),
        }


# =========================
# Software & SQL Problem Solver Agent
# =========================

class SQLSolverAgent:
    def __init__(self):
        self.llm = get_llm(temperature=0.1)

    def run(self, task_description: str) -> dict:
        prompt = (
            "You are a senior software troubleshooting and SQL expert.\n\n"
            f"Task:\n{task_description}\n\n"
            "Rules:\n"
            "- If it's a software/code error: identify root cause, then give the exact fix.\n"
            "- If it's a SQL problem: write optimized, correct SQL queries (specify dialect if known).\n"
            "- Always explain the fix in 2-3 short technical lines.\n"
            "- Wrap all code/SQL inside proper fenced code blocks.\n"
            "- Do not give vague answers, be precise and production-ready."
        )
        resp = self.llm.invoke(prompt)
        return {
            "content": resp.content.strip(),
            "usage": extract_usage(resp),
        }