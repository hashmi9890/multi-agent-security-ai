import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

def get_llm(temperature=0.0):
    """Returns the Groq LLM instance (Llama 3.3)."""
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # Error handling agar .env mein key na ho
    if not groq_api_key:
        raise ValueError("🚨 ERROR: GROQ_API_KEY is missing in your .env file!")

    # Groq ka Model return kar raha hai
    return ChatGroq(
        model=groq_model,
        temperature=temperature,
        api_key=groq_api_key
    )