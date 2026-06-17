class ConversationMemory:
    """
    Simple in-memory conversation storage.
    """

    def __init__(self):
        self.history = []

    def add(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    def get_context(self) -> str:
        formatted = ""
        for item in self.history:
            formatted += f"{item['role'].upper()}: {item['content']}\n"
        return formatted.strip()

    def clear(self):
        self.history = []