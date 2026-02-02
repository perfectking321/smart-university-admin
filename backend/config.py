import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "sqlcoder:7b")  # Changed to 7B for faster inference
    CACHE_SIZE = 100  # Maximum cached queries
    QUERY_TIMEOUT = 60  # seconds (reduced for smaller model)
    KEEP_ALIVE = "30m"  # Keep model loaded in memory

config = Config()
