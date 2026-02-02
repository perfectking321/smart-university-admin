# 🎓 Smart University Administrator

An AI-powered natural language interface for university database management using Ollama's SQLCoder model.

## 🚀 Features

- **Natural Language Queries**: Ask questions in plain English
- **AI-Powered SQL Generation**: SQLCoder 15B model converts questions to SQL
- **Query Caching**: Instant results for repeated queries
- **Real-time Results**: Beautiful table display with execution stats
- **Safe Execution**: Only SELECT queries allowed, SQL injection protection
- **Rich Database**: 500+ students, 6 departments, comprehensive data

## 📋 Prerequisites

- **Python 3.10+**
- **PostgreSQL 14+**
- **Ollama** with SQLCoder 15B model
- **16GB+ RAM** (32GB recommended)
- **GPU recommended** (12GB+ VRAM for faster inference)

## 🛠️ Installation

### 1. Install PostgreSQL (Arch Linux)
```bash
sudo pacman -S postgresql
sudo -u postgres initdb -D /var/lib/postgres/data
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Install Ollama
```bash
curl https://ollama.ai/install.sh | sh
ollama pull sqlcoder:15b
```

### 3. Setup Database
```bash
# Set postgres password
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres123';"

# Create database
sudo -u postgres psql -c "CREATE DATABASE university_db;"

# Run schema
sudo -u postgres psql -d university_db -f database/schema.sql

# Generate sample data
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ../database
python generate_fake_data.py
```

### 4. Configure Environment
Edit `backend/.env`:
```env
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/university_db
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=sqlcoder:15b
```

## 🎯 Running the Application

**Terminal 1 - Ollama:**
```bash
ollama serve
```

**Terminal 2 - Backend:**
```bash
cd backend
source venv/bin/activate
python main.py
```

**Terminal 3 - Frontend:**
```bash
cd frontend
python -m http.server 3000
```

**Open Browser:**
http://localhost:3000

## 💡 Example Queries

- "Show all students in Computer Science department"
- "What is the average GPA by department?"
- "List students with GPA above 3.5"
- "Show placement statistics for each department"
- "Students with attendance below 75%"
- "Top 10 students by GPA"

## 📊 Database Schema

### Tables
- **students** - Student information with GPA, department, hostel
- **departments** - Academic departments with HOD
- **courses** - Course catalog with credits and semester
- **enrollments** - Student-course relationships
- **attendance** - Daily attendance records
- **grades** - Exam scores and grades
- **hostels** - Hostel accommodation details
- **placements** - Job placement records

### Key Relationships
- Students → Departments (via department_id)
- Students → Hostels (via hostel_id)
- Students ↔ Courses (via enrollments)
- Attendance/Grades → Students + Courses

## ⚙️ API Endpoints

- `POST /api/query` - Execute natural language query
- `GET /api/health` - Health check
- `GET /api/tables` - List all tables
- `GET /api/cache/stats` - Cache statistics
- `DELETE /api/cache/clear` - Clear cache

## 🔧 Configuration

### Backend (config.py)
```python
DATABASE_URL = "postgresql://..."
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "sqlcoder:15b"
CACHE_SIZE = 100
QUERY_TIMEOUT = 120  # seconds
```

### Performance Tips
- First query takes 30-60s (model loading)
- Subsequent queries are much faster
- Cached queries return instantly
- Use GPU for 5-10x faster inference

## 🛡️ Security Features

- ✅ SQL injection protection
- ✅ Only SELECT queries allowed
- ✅ Dangerous keywords blocked
- ✅ Query validation before execution
- ✅ Schema-aware query generation

## 📝 Project Structure

```
smart-university-admin/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── database.py          # Database connection
│   ├── cache.py             # Query caching
│   ├── schema_optimizer.py  # Schema analysis
│   ├── sql_validator.py     # SQL validation
│   ├── ollama_client.py     # Ollama API client
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── index.html          # Main UI
│   ├── style.css           # Styling
│   └── app.js              # Frontend logic
├── database/
│   ├── schema.sql          # Database schema
│   └── generate_fake_data.py  # Sample data generator
└── ollama/
    └── system_prompt.txt   # AI system prompt
```

## 🐛 Troubleshooting

### Backend not starting
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Check PostgreSQL
sudo systemctl status postgresql
```

### Slow queries
- First query loads the model (30-60s)
- Use GPU for faster inference
- Consider using smaller model: `ollama pull sqlcoder:7b`

### Connection errors
```bash
# Verify all services
curl http://localhost:8000/api/health
curl http://localhost:11434/api/tags
curl http://localhost:3000
```

## 🎨 Technologies Used

- **Backend**: FastAPI, PostgreSQL, psycopg2
- **AI**: Ollama (SQLCoder 15B)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Database**: PostgreSQL 18
- **Data Generation**: Faker library

## 📄 License

Educational project for DBMS course.

## 👥 Contributors

Developed as part of DBMS Project coursework.

## 🙏 Acknowledgments

- Ollama for local LLM inference
- SQLCoder model by Defog.ai
- FastAPI framework
- PostgreSQL database

---

**⚡ Quick Start:** Run all three terminals, open http://localhost:3000, and ask "Show all students" - that's it! 🚀
