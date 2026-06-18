from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    MAX_MEMORY_HISTORY: int = int(os.getenv("MAX_MEMORY_HISTORY", "50"))
    PERSIST_DIR: str = "data/memory"