"""
Vector-based schema linking for faster and more accurate table selection
Uses embeddings and cosine similarity instead of keyword matching
"""

import numpy as np
from typing import List, Dict, Set
from database import db

try:
    from sentence_transformers import SentenceTransformer
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False

class VectorSchemaOptimizer:
    def __init__(self):
        self.full_schema = None
        self.schema_cache = None
        self.table_embeddings = {}
        self.table_descriptions = {
            "students": "student information including name, roll number, email, phone, GPA, department, hostel, admission year",
            "departments": "department details with name, head of department, building location",
            "courses": "course information including code, name, credits, department, semester",
            "attendance": "student attendance records with date and present/absent status for each course",
            "grades": "student exam grades and scores including midterm, final, quiz results",
            "hostels": "hostel accommodation information with capacity and warden details",
            "placements": "student placement data including company, job role, package, placement date",
            "enrollments": "student course enrollment records linking students to courses"
        }
        
        # Fallback keyword matching (same as before)
        self.table_keywords = {
            "students": ["student", "name", "gpa", "grade", "enrollment"],
            "departments": ["department", "dept", "hod", "faculty"],
            "courses": ["course", "subject", "class"],
            "attendance": ["attendance", "present", "absent", "attend"],
            "grades": ["grade", "score", "marks", "result", "exam"],
            "hostels": ["hostel", "room", "accommodation", "residence"],
            "placements": ["placement", "job", "company", "recruit", "placed"],
            "enrollments": ["enrollment", "enrolled", "taking", "registered"]
        }
        
        if DEPS_AVAILABLE:
            print("🔄 Loading embedding model for schema linking...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self._precompute_table_embeddings()
            print("✅ Vector schema optimizer initialized")
        else:
            self.model = None
            print("⚠️ Using keyword-based schema linking (install sentence-transformers for better performance)")
    
    def _normalize_vector(self, vector):
        """Normalize vector for cosine similarity"""
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm
    
    def _precompute_table_embeddings(self):
        """Pre-compute embeddings for all table descriptions"""
        if not DEPS_AVAILABLE or self.model is None:
            return
        
        for table, description in self.table_descriptions.items():
            embedding = self.model.encode(description, convert_to_numpy=True)
            self.table_embeddings[table] = self._normalize_vector(embedding)
        
        print(f"📊 Pre-computed embeddings for {len(self.table_embeddings)} tables")
    
    def load_schema(self):
        """Load complete database schema once and cache it"""
        if self.schema_cache is not None:
            self.full_schema = self.schema_cache
            return
            
        if not self.full_schema:
            schema_data = db.get_schema()
            self.full_schema = {}
            
            for row in schema_data["rows"]:
                table_name = row["table_name"]
                columns = row["columns"]
                self.full_schema[table_name] = columns
            
            self.schema_cache = self.full_schema.copy()
            print("✅ Schema loaded and cached in memory")
    
    def _get_relevant_tables_vector(self, question: str, top_k: int = 4) -> List[str]:
        """
        Use vector similarity to find relevant tables
        
        Args:
            question: User's natural language question
            top_k: Number of most relevant tables to return
            
        Returns:
            List of relevant table names
        """
        if not DEPS_AVAILABLE or self.model is None:
            return self._get_relevant_tables_keyword(question)
        
        # Generate embedding for question
        question_embedding = self.model.encode(question.lower(), convert_to_numpy=True)
        question_embedding = self._normalize_vector(question_embedding)
        
        # Calculate similarity with each table
        similarities = {}
        for table, table_embedding in self.table_embeddings.items():
            if table in self.full_schema:
                # Cosine similarity (dot product of normalized vectors)
                similarity = np.dot(question_embedding, table_embedding)
                similarities[table] = float(similarity)
        
        # Sort by similarity and get top_k
        sorted_tables = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        relevant_tables = [table for table, score in sorted_tables[:top_k] if score > 0.3]
        
        # Always include enrollments if both students and courses are relevant
        if "students" in relevant_tables and "courses" in relevant_tables:
            if "enrollments" not in relevant_tables:
                relevant_tables.append("enrollments")
        
        print(f"🎯 Vector-selected tables: {relevant_tables}")
        return relevant_tables
    
    def _get_relevant_tables_keyword(self, question: str) -> List[str]:
        """
        Fallback keyword-based table selection
        """
        question_lower = question.lower()
        relevant_tables = []
        
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
        
        print(f"🔍 Keyword-selected tables: {relevant_tables}")
        return relevant_tables
    
    def get_relevant_tables(self, question: str) -> str:
        """
        Detect relevant tables and build schema context
        
        Args:
            question: User's natural language question
            
        Returns:
            Formatted schema text with only relevant tables
        """
        self.load_schema()
        
        # Get relevant tables using vector similarity
        relevant_tables = self._get_relevant_tables_vector(question)
        
        # Build minimal schema string
        schema_text = "Database Schema:\n\n"
        for table in relevant_tables:
            if table in self.full_schema:
                schema_text += f"Table: {table}\n"
                schema_text += f"Columns: {', '.join(self.full_schema[table])}\n\n"
        
        # Add relationship hints (minimal version)
        schema_text += "\nRelationships:\n"
        if "students" in relevant_tables and "departments" in relevant_tables:
            schema_text += "- students.department_id -> departments.id\n"
        if "students" in relevant_tables and "hostels" in relevant_tables:
            schema_text += "- students.hostel_id -> hostels.id\n"
        if "courses" in relevant_tables and "departments" in relevant_tables:
            schema_text += "- courses.department_id -> departments.id\n"
        if "enrollments" in relevant_tables:
            schema_text += "- enrollments.student_id -> students.id\n"
            schema_text += "- enrollments.course_id -> courses.id\n"
        if "attendance" in relevant_tables:
            schema_text += "- attendance.student_id -> students.id\n"
            schema_text += "- attendance.course_id -> courses.id\n"
        if "grades" in relevant_tables:
            schema_text += "- grades.student_id -> students.id\n"
            schema_text += "- grades.course_id -> courses.id\n"
        if "placements" in relevant_tables:
            schema_text += "- placements.student_id -> students.id\n"
        
        return schema_text

# Global vector optimizer instance
vector_optimizer = VectorSchemaOptimizer()
