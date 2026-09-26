import os

APP_NAME = "Kavshara"
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
MODEL = os.getenv("KAVSHARA_MODEL", "qwen2.5:3b")
TEMPERATURE = float(os.getenv("KAVSHARA_TEMPERATURE", "0.4"))
MEMORY_FILE = os.getenv("KAVSHARA_MEMORY_FILE", "data/memory.json")
MAX_MEMORY_ITEMS = int(os.getenv("KAVSHARA_MAX_MEMORY", "100"))

SYSTEM_PROMPT = """You are Kavshara, a local-first personal AI assistant.
Be concise, practical, and honest.
You can reason about the user's request and use the tools exposed by the application.
Do not claim an action was completed unless the application actually completed it.
When a task is ambiguous, ask for the minimum clarification needed.
"""
