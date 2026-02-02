from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
from sse_starlette.sse import EventSourceResponse
import time
import json
import asyncio

from database import db
from schema_optimizer import optimizer
from vector_schema import vector_optimizer
from sql_validator import validator
from llm_service import llm_service
from llm_middleware import caching_middleware

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
    if not await llm_service.test_connection():
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
    await llm_service.close()

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
/stream")
async def query_database_stream(request: QueryRequest):
    """
    Streaming endpoint using SSE (Server-Sent Events)
    Based on Vanna AI's streaming architecture for real-time responses
    """
    
    async def generate_stream():
        """Generate SSE stream with progressive updates"""
        start_time = time.time()
        
        try:
            question = request.question.strip()
            
            if not question:
                yield {
                    "event": "error",
                    "data": json.dumps({"message": "Question cannot be empty"})
                }
                return
            
            # Step 1: Check cache
            yield {
                "event": "progress",
                "data": json.dumps({"stage": "cache_check", "message": "Checking cache..."})
            }
            
            schema_text = vector_optimizer.get_relevant_tables(question)
            cached_result = await caching_middleware.before_request(question, schema_text)
            
            if cached_result:
                # Cache hit! Return immediately
                cached_result["execution_time"] = time.time() - start_time
                yield {
                    "event": "complete",
                    "data": json.dumps(cached_result)
                }
                return
            
            # Step 2: Schema linking
            yield {
                "event": "progress",
                "data": json.dumps({"stage": "schema", "message": "Finding relevant tables..."})
            }
            await asyncio.sleep(0.1)  # Allow UI to update
            
            # Step 3: SQL Generation (streaming)
            yield {
                "event": "progress",
                "data": jso from middleware"""
    return caching_middleware.stats()

@app.delete("/api/cache/clear")
async def clear_cache():
    """Clear all cached queries"""
    caching_middlewar           "token": chunk["content"],
                            "accumulated": chunk["accumulated"]
                        })
                    }
                
                elif chunk["type"] == "complete":
                    sql = chunk["sql"]
                    yield {
                        "event": "sql_complete",
                        "data": json.dumps({"sql": sql})
                    }
    ollama_status = await llm_service.test_connection()
    return {
        "status": "healthy",
        "database": "connected" if db.connection_pool else "disconnected",
        "ollama": "connected" if ollama_status else "disconnected",
        "cache": caching_middleware.stats()
                        "data": json.dumps({"message": chunk["message"]})
                    }
                    return
            
            # Step 4: Validate SQL
            yield {
                "event": "progress",
                "data": json.dumps({"stage": "validation", "message": "Validating query..."})
            }
            
            is_safe, message = validator.is_safe_query(sql)
            if not is_safe:
                yield {
                    "event": "error",
                    "data": json.dumps({"message": f"Unsafe query: {message}"})
                }
                return
            
            # Step 5: Execute SQL
            yield {
                "event": "progress",
                "data": json.dumps({"stage": "execution", "message": "Executing query..."})
            }
            
            results = db.execute_query(sql)
            
            # Step 6: Send complete response
            response = {
                "sql": sql,
                "results": results,
                "cached": False,
                "execution_time": time.time() - start_time
            }
            
            # Cache for future requests
            await caching_middleware.after_response(question, schema_text, sql, results)
            
            yield {
                "event": "complete",
                "data": json.dumps(response)
            }
        
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)})
            }
    
    return EventSourceResponse(generate_stream())


@app.post("/api/query", response_model=QueryResponse)
async def query_database(request: QueryRequest):
    """
    Non-streaming endpoint (backward compatibility)
    For clients that don't support SSE
    """
    start_time = time.time()
    
    try:
        question = request.question.strip()
        
        if not question:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Check cache via middleware
        schema_text = vector_optimizer.get_relevant_tables(question)
        cached_result = await caching_middleware.before_request(question, schema_text)
        
        if cached_result:
            cached_result["execution_time"] = time.time() - start_time
            return cached_result
        
        # Generate SQL using async LLM service
        sql = await llm_service.generate_sql(question, schema_text)
        
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
        
        # Cache via middleware
        await caching_middleware.after_response(question, schema_textantic similarity
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
