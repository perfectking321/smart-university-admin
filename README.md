# Smart University Administrator

A full‑stack **Smart University Admin** system that lets you ask questions about a university database in plain English, then:

1) Uses **Ollama (SQLCoder)** to generate a **PostgreSQL `SELECT` query**  
2) Validates the SQL for safety (blocks destructive queries / injection patterns)  
3) Executes the query on **PostgreSQL**  
4) Displays the generated SQL + results in a simple **web UI**  
5) Caches repeated questions for faster responses

---

## Features

- **Natural language → SQL** using Ollama (`sqlcoder` model)
- **Safe querying only**: validator restricts to `SELECT` and blocks dangerous keywords/patterns
- **Schema-aware prompting** (loads DB schema and selects relevant tables)
- **FastAPI backend** with clean API endpoints
- **Modern React frontend** with TypeScript, Vite, and Tailwind CSS to chat, view SQL, and render results table
- **Query caching** (LRU-style) for repeated questions
- **Fake data generator** for quick demos

---

## Tech Stack

**Backend**
- Python 3.10+
- FastAPI
- Uvicorn
- PostgreSQL (psycopg2)
- python-dotenv
- Requests

**LLM / SQL Generation**
- Ollama
- Model: `sqlcoder` (example: `sqlcoder:15b`)

**Frontend**
- React 19 + TypeScript
- Vite (build tool)
- Tailwind CSS
- Spline 3D integration
- Motion (animations)

---

## Repository Structure

- `backend/` — FastAPI app + DB access + schema optimizer + SQL validation + Ollama client  
- `frontend/` — Modern React frontend with TypeScript, Vite, and Tailwind CSS  
- `database/` — SQL schema + fake data generator  
- `ollama/` — prompt/system instructions for SQL generation  
- `File.md` — full implementation/guide (source document)

---

## Prerequisites

- **Python** 3.10+
- **Node.js** 18+ and npm
- **PostgreSQL** 14+
- **Ollama** installed and running
- (Recommended) Enough RAM/VRAM for the chosen SQLCoder model

---

## Quick Start

### 1) Clone the repo
```bash
git clone https://github.com/perfectking321/smart-university-admin.git
cd smart-university-admin
```

### 2) Set up PostgreSQL database
Create a database (example name: `university_db`) and apply the schema:

```bash
# inside psql:
CREATE DATABASE university_db;
\c university_db
\i /path/to/your/repo/database/schema.sql
```

### 3) (Optional) Generate fake data
```bash
cd database
# Edit DATABASE_URL inside generate_fake_data.py to match your password/host
python generate_fake_data.py
```

### 4) Pull the Ollama SQLCoder model
```bash
ollama pull sqlcoder:15b
# or a smaller one if needed:
# ollama pull sqlcoder:7b
```

### 5) Configure backend environment
Create `backend/.env`:
```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/university_db
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=sqlcoder:15b
```

### 6) Install backend dependencies + run API
```bash
cd backend
python -m venv venv

# Activate:
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
python main.py
```

Backend should be available at:
- `http://localhost:8000`

Health check:
- `http://localhost:8000/api/health`

### 7) Set up and run the frontend
Create `frontend/.env.local`:
```env
VITE_API_BASE_URL=http://localhost:8000/api
```

Install dependencies and start the development server:
```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at:
- `http://localhost:3000`

---

## How It Works (High Level)

1. Frontend sends `{ question }` to `POST /api/query`
2. Backend loads relevant schema info for the question
3. Ollama generates SQL from prompt + schema
4. SQL is validated (only safe `SELECT` allowed)
5. SQL executes on PostgreSQL
6. Response returns:
   - generated SQL
   - rows/columns
   - execution time
   - whether cached

---

## API Endpoints

- `POST /api/query`  
  Body:
  ```json
  { "question": "What is the average GPA by department?" }
  ```

- `GET /api/health` — service status
- `GET /api/tables` — list tables detected from schema
- `GET /api/cache/stats` — cache size info
- `DELETE /api/cache/clear` — clears cache

---

## Example Questions

- “Show all students in Computer Science department”
- “What is the average GPA by department?”
- “List students with attendance below 75%”
- “Show placement statistics for each department”
- “Top 10 students by GPA with their department names”

---

## Security Notes

- This project is designed for **read-only analytics**.
- The SQL validator blocks destructive statements (e.g., `DROP`, `DELETE`, `UPDATE`, etc.) and common injection patterns.
- If you want production readiness, add:
  - authentication/authorization
  - request rate limiting
  - strict CORS config (don’t use `*`)
  - structured logging + monitoring
  - safer DB credentials handling / secrets manager

---

## Troubleshooting

### Backend says “Ollama not available”
Make sure Ollama is running:
```bash
ollama serve
ollama list
```

### Database connection fails
Check:
- PostgreSQL is running
- `DATABASE_URL` is correct in `backend/.env`
- schema was applied to the target database

### Frontend can’t reach backend
- Confirm backend is running on `http://localhost:8000`
- Try:
```bash
curl http://localhost:8000/api/health
```

---

## License

No license file is currently detected in the repository. Add a `LICENSE` file if you want to declare usage terms.

---

## Acknowledgements

- Ollama for local model serving
- SQLCoder model for text-to-SQL generation
