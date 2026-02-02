"""
LLM Service - Async Ollama client with streaming support
Based on Vanna AI architecture for high-performance LLM interactions
"""

import aiohttp
import asyncio
import json
from typing import AsyncGenerator, Optional, Dict, Any
from config import config


class LLMService:
    """Async LLM service for streaming responses from Ollama"""
    
    def __init__(self):
        self.api_url = f"{config.OLLAMA_HOST}/api/generate"
        self.chat_url = f"{config.OLLAMA_HOST}/api/chat"
        self.model = config.OLLAMA_MODEL
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=config.QUERY_TIMEOUT)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def stream_sql_generation(
        self, 
        question: str, 
        schema_text: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream SQL generation with progress updates
        Yields chunks as they arrive from LLM
        """
        prompt = f"""{schema_text}

Question: {question}

Generate PostgreSQL SELECT query. Output ONLY SQL, no explanation."""
        
        session = await self._get_session()
        
        try:
            async with session.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True,
                    "keep_alive": config.KEEP_ALIVE,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9,
                        "num_predict": 512
                    }
                }
            ) as response:
                response.raise_for_status()
                
                accumulated_sql = ""
                
                # Stream chunks
                async for line in response.content:
                    if line:
                        try:
                            chunk = json.loads(line)
                            
                            if "response" in chunk:
                                token = chunk["response"]
                                accumulated_sql += token
                                
                                # Yield progress chunk
                                yield {
                                    "type": "token",
                                    "content": token,
                                    "accumulated": accumulated_sql
                                }
                            
                            # Check if done
                            if chunk.get("done", False):
                                # Clean and yield final SQL
                                cleaned_sql = self._clean_sql(accumulated_sql)
                                yield {
                                    "type": "complete",
                                    "sql": cleaned_sql,
                                    "model": self.model
                                }
                                break
                                
                        except json.JSONDecodeError:
                            continue
        
        except asyncio.TimeoutError:
            yield {
                "type": "error",
                "message": "LLM request timed out"
            }
        except Exception as e:
            yield {
                "type": "error",
                "message": f"LLM error: {str(e)}"
            }
    
    async def generate_sql(self, question: str, schema_text: str) -> str:
        """
        Non-streaming SQL generation (for backward compatibility)
        """
        prompt = f"""{schema_text}

Question: {question}

Generate PostgreSQL SELECT query. Output ONLY SQL, no explanation."""
        
        session = await self._get_session()
        
        try:
            async with session.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "keep_alive": config.KEEP_ALIVE,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9,
                        "num_predict": 512
                    }
                }
            ) as response:
                response.raise_for_status()
                result = await response.json()
                sql = result.get("response", "").strip()
                return self._clean_sql(sql)
        
        except asyncio.TimeoutError:
            raise Exception("Ollama request timed out")
        except Exception as e:
            raise Exception(f"Ollama API error: {str(e)}")
    
    def _clean_sql(self, sql: str) -> str:
        """Clean SQL output from LLM"""
        sql = sql.replace("```sql", "").replace("```", "")
        sql = " ".join(sql.split())
        sql = sql.rstrip(";")
        return sql
    
    async def test_connection(self) -> bool:
        """Test if Ollama is running"""
        try:
            session = await self._get_session()
            async with session.get(f"{config.OLLAMA_HOST}/api/tags") as response:
                return response.status == 200
        except:
            return False


# Global LLM service instance
llm_service = LLMService()
