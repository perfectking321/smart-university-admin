from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import time

from database import db
from cache import cache
from schema_optimizer import optimizer
from semantic_cache import semantic_cache
from vector_schema import vector_optimizer
from sql_validator import validator
from ollama_client import ollama_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    print("🚀 Starting Smart University Admin API...")
    
    # Test database connection
    try:
        db.connect()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise
    
    # Test Ollama connection
    if not ollama_client.test_connection():
        print("❌ Ollama is not running. Start Ollama first!")
        raise Exception("Ollama not available")
    else:
        print("✅ Ollama connected successfully")
    
    # Load database schema
    optimizer.load_schema()
    print("✅ Database schema loaded")
    
    print("✅ API ready at http://localhost:8000")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Smart University Admin API...")

# Initialize FastAPI app with lifespan
app = FastAPI(title="Smart University Admin API", lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class QueryRequest(BaseModel):
    question: str

# Response model
class QueryResponse(BaseModel):
    sql: str
    results: dict
    cached: bool
    execution_time: float

@app.post("/api/query", response_model=QueryResponse)
async def query_database(request: QueryRequest):
    """Main endpoint: Convert natural language to SQL and execute"""
    start_time = time.time()
    
    try:
        question = request.question.strip()
        
        if not question:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Check semantic cache first
        cached_result = semantic_cache.get(question)
        if cached_result:
            cached_result["execution_time"] = time.time() - start_time
            return cached_result
        
        # Get relevant tables using vector-based schema linking
        schema_text = vector_optimizer.get_relevant_tables(question)
        
        # Generate SQL using Ollama
        sql = ollama_client.generate_sql(question, schema_text)
        
        # Validate SQL
        is_safe, message = validator.is_safe_query(sql)
        if not is_safe:
            raise HTTPException(status_code=400, detail=f"Unsafe query: {message}")
        
        # Execute SQL
        results = db.execute_query(sql)
        
        # Prepare response
        response = {
            "sql": sql,
            "results": results,
            "cached": False,
            "execution_time": time.time() - start_time
        }
        
        # Cache the result with semantic similarity
        semantic_cache.set(question, sql, results)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    return {
        "cache_size": semantic_cache.size(),
        "max_size": semantic_cache.max_size,
        "cache_type": "semantic"
    }

@app.delete("/api/cache/clear")
async def clear_cache():
    """Clear all cached queries"""
    semantic_cache.clear()
    return {"message": "Cache cleared successfully"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected" if db.connection_pool else "disconnected",
        "ollama": "connected" if ollama_client.test_connection() else "disconnected"
    }

@app.get("/api/tables")
async def get_tables():
    """Get list of all database tables"""
    optimizer.load_schema()
    return {
        "tables": list(optimizer.full_schema.keys())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
