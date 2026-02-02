import psycopg2
from psycopg2.extras import RealDictCursor
from config import config

class Database:
    def __init__(self):
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(
                config.DATABASE_URL,
                cursor_factory=RealDictCursor
            )
            print("✅ Database connected successfully")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    def execute_query(self, sql):
        """Execute SQL query and return results"""
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.cursor()
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
                self.connection.commit()
                return {"message": "Query executed successfully"}
                
        except Exception as e:
            self.connection.rollback()
            print(f"❌ Query execution failed: {e}")
            raise
        finally:
            cursor.close()
    
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
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("Database connection closed")

# Global database instance
db = Database()
