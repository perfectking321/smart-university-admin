import re

class SQLValidator:
    # Dangerous SQL keywords that modify data
    DANGEROUS_KEYWORDS = [
        "DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE", 
        "INSERT", "UPDATE", "GRANT", "REVOKE"
    ]
    
    # SQL injection patterns
    INJECTION_PATTERNS = [
        r";\s*DROP",
        r";\s*DELETE",
        r"--",
        r"/\*",
        r"\*/",
        r"xp_",
        r"sp_",
        r"exec\s*\(",
    ]
    
    def is_safe_query(self, sql):
        """Validate if SQL query is safe to execute"""
        sql_upper = sql.upper()
        
        # Check for dangerous keywords
        for keyword in self.DANGEROUS_KEYWORDS:
            if keyword in sql_upper:
                return False, f"Dangerous keyword detected: {keyword}"
        
        # Check for SQL injection patterns
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, sql, re.IGNORECASE):
                return False, f"Potential SQL injection detected"
        
        # Must start with SELECT
        if not sql_upper.strip().startswith("SELECT"):
            return False, "Only SELECT queries are allowed"
        
        return True, "Query is safe"
    
    def sanitize_sql(self, sql):
        """Remove comments and extra whitespace"""
        # Remove single-line comments
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        # Remove multi-line comments
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        # Remove extra whitespace
        sql = ' '.join(sql.split())
        return sql

# Global validator instance
validator = SQLValidator()
