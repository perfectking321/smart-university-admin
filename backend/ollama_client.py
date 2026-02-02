import requests
import json
from config import config

class OllamaClient:
    def __init__(self):
        self.api_url = f"{config.OLLAMA_HOST}/api/generate"
        self.model = config.OLLAMA_MODEL
    
    def generate_sql(self, user_question, schema_text):
        """Generate SQL from natural language question"""
        
        # Build prompt
        prompt = f"""{schema_text}

Instructions:
- Generate ONLY the SQL query, no explanations
- Use proper PostgreSQL syntax
- Include appropriate JOINs, WHERE clauses, and aggregations
- Return ONLY valid SELECT statements
- Do not include markdown code blocks or formatting

User Question: {user_question}

SQL Query:"""
        
        try:
            # Call Ollama API
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Low temperature for deterministic output
                        "top_p": 0.9
                    }
                },
                timeout=config.QUERY_TIMEOUT
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract SQL from response
            sql = result.get("response", "").strip()
            
            # Clean up the SQL
            sql = self._clean_sql(sql)
            
            return sql
            
        except requests.exceptions.Timeout:
            raise Exception("Ollama request timed out")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API error: {str(e)}")
    
    def _clean_sql(self, sql):
        """Clean SQL output from LLM"""
        # Remove markdown code blocks
        sql = sql.replace("```sql", "").replace("```", "")
        # Remove extra whitespace
        sql = " ".join(sql.split())
        # Remove trailing semicolon if exists
        sql = sql.rstrip(";")
        return sql
    
    def test_connection(self):
        """Test if Ollama is running"""
        try:
            response = requests.get(f"{config.OLLAMA_HOST}/api/tags")
            return response.status_code == 200
        except:
            return False

# Global Ollama client
ollama_client = OllamaClient()
