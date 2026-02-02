from database import db

class SchemaOptimizer:
    def __init__(self):
        self.full_schema = None
        self.table_keywords = {
            "students": ["student", "name", "gpa", "grade", "enrollment"],
            "departments": ["department", "dept", "hod", "faculty"],
            "courses": ["course", "subject", "class"],
            "attendance": ["attendance", "present", "absent", "attend"],
            "grades": ["grade", "score", "marks", "result", "exam"],
            "hostels": ["hostel", "room", "accommodation", "residence"],
            "placements": ["placement", "job", "company", "recruit", "placed"]
        }
    
    def load_schema(self):
        """Load complete database schema"""
        if not self.full_schema:
            schema_data = db.get_schema()
            self.full_schema = {}
            
            for row in schema_data["rows"]:
                table_name = row["table_name"]
                columns = row["columns"]
                self.full_schema[table_name] = columns
    
    def get_relevant_tables(self, question):
        """Detect relevant tables from user question"""
        self.load_schema()
        
        question_lower = question.lower()
        relevant_tables = []
        
        # Check each table's keywords
        for table, keywords in self.table_keywords.items():
            if table in self.full_schema:
                for keyword in keywords:
                    if keyword in question_lower:
                        relevant_tables.append(table)
                        break
        
        # If no tables found, return all tables
        if not relevant_tables:
            relevant_tables = list(self.full_schema.keys())
        
        # Build schema string for selected tables
        schema_text = "Database Schema:\n\n"
        for table in relevant_tables:
            if table in self.full_schema:
                schema_text += f"Table: {table}\n"
                schema_text += f"Columns: {', '.join(self.full_schema[table])}\n\n"
        
        return schema_text

# Global optimizer instance
optimizer = SchemaOptimizer()
