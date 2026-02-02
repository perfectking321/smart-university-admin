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
        
        # Always include enrollments if both students and courses are mentioned
        if "students" in relevant_tables and "courses" in relevant_tables:
            if "enrollments" not in relevant_tables:
                relevant_tables.append("enrollments")
        
        # If no tables found, return all tables
        if not relevant_tables:
            relevant_tables = list(self.full_schema.keys())
        
        # Build schema string for selected tables with relationships
        schema_text = "Database Schema:\n\n"
        for table in relevant_tables:
            if table in self.full_schema:
                schema_text += f"Table: {table}\n"
                schema_text += f"Columns: {', '.join(self.full_schema[table])}\n\n"
        
        # Add relationship hints
        schema_text += "\nTable Relationships:\n"
        schema_text += "- students.department_id -> departments.id\n"
        schema_text += "- students.hostel_id -> hostels.id\n"
        schema_text += "- courses.department_id -> departments.id\n"
        schema_text += "- enrollments.student_id -> students.id\n"
        schema_text += "- enrollments.course_id -> courses.id\n"
        schema_text += "- attendance.student_id -> students.id\n"
        schema_text += "- attendance.course_id -> courses.id\n"
        schema_text += "- grades.student_id -> students.id\n"
        schema_text += "- grades.course_id -> courses.id\n"
        schema_text += "- placements.student_id -> students.id\n"
        schema_text += "\nIMPORTANT: To join students with courses, use the enrollments table!\n"
        
        return schema_text

# Global optimizer instance
optimizer = SchemaOptimizer()
