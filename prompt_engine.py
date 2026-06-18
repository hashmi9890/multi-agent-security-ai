from typing import Dict
from dataclasses import dataclass

@dataclass
class PromptTemplate:
    system: str
    user: str

class PromptEngine:
    TEMPLATES: Dict[str, PromptTemplate] = {
        "general": PromptTemplate(
            system="You are a helpful AI assistant. Be concise and accurate.",
            user="Context:\n{context}\n\nUser: {input}\nAssistant:"
        ),
        "coder": PromptTemplate(
            system="You are an expert Python developer. Provide clean, production-ready code with comments.",
            user="Context:\n{context}\n\nRequest: {input}\n\nCode/Explanation:"
        ),
        "analyst": PromptTemplate(
            system="You are a data analyst. Provide insights, trends, and actionable recommendations.",
            user="Context:\n{context}\n\nQuery: {input}\n\nAnalysis:"
        ),
        "creative": PromptTemplate(
            system="You are a creative writer. Be imaginative, engaging, and original.",
            user="Context:\n{context}\n\nPrompt: {input}\n\nResponse:"
        )
    }

    @staticmethod
    def build(intent: str, user_input: str, context: str) -> Dict[str, str]:
        template = PromptEngine.TEMPLATES.get(intent, PromptEngine.TEMPLATES["general"])
        return {
            "system": template.system,
            "user": template.user.format(context=context, input=user_input)
        }

    @staticmethod
    def list_intents() -> list:
        return list(PromptEngine.TEMPLATES.keys())