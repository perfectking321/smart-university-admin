import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "sqlcoder:15b")
    CACHE_SIZE = 100  # Maximum cached queries
    QUERY_TIMEOUT = 120  # seconds (increased for large models)

config = Config()
