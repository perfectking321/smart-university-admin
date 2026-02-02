import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
from config import config

class Database:
    def __init__(self):
        self.connection_pool = None
    
    def connect(self):
        """Establish database connection pool"""
        try:
            self.connection_pool = pool.SimpleConnectionPool(
                1,  # minimum connections
                10,  # maximum connections
                config.DATABASE_URL,
                cursor_factory=RealDictCursor
            )
            print("✅ Database connection pool created successfully")
        except Exception as e:
            print(f"❌ Database connection pool creation failed: {e}")
            raise
    
    def execute_query(self, sql):
        """Execute SQL query and return results using connection pool"""
        if not self.connection_pool:
            self.connect()
        
        # Auto-add LIMIT if not present (prevents massive result sets)
        # Skip if query has GROUP BY, LIMIT, or aggregation functions
        sql_upper = sql.upper().strip()
        if (sql_upper.startswith('SELECT') and 
            'LIMIT' not in sql_upper and 
            'GROUP BY' not in sql_upper):
            sql = f"{sql} LIMIT 1000"
        
        connection = None
        cursor = None
        try:
            connection = self.connection_pool.getconn()
            cursor = connection.cursor()
            cursor.execute(sql)
            
            # Check if query returns data
            if cursor.description:
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return {
                    "columns": columns,
                    "rows": results,
                    "row_count": len(results)
                }
            else:
                connection.commit()
                return {"message": "Query executed successfully"}
                
        except Exception as e:
            if connection:
                connection.rollback()
            print(f"❌ Query execution failed: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.connection_pool.putconn(connection)
    
    def get_schema(self):
        """Get database schema for all tables"""
        query = """
        SELECT 
            t.table_name,
            array_agg(c.column_name || ' ' || c.data_type) as columns
        FROM information_schema.tables t
        JOIN information_schema.columns c 
            ON t.table_name = c.table_name
        WHERE t.table_schema = 'public'
        GROUP BY t.table_name
        ORDER BY t.table_name;
        """
        return self.execute_query(query)
    
    def close(self):
        """Close database connection pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("Database connection pool closed")

# Global database instance
db = Database()
