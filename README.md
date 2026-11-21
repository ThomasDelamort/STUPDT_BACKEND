# StuPDT Backend API

High-performance satirical backend API powering the **StuPDT Bureaucracy Platform**.

Built with **FastAPI**, **PostgreSQL** (`asyncpg` + `SQLAlchemy 2.0 AsyncIO`), and **Groq Cloud AI** (with fallback to Google Gemini and offline satirical templates).

---

## Features

- **Groq Cloud AI**: Powered by `openai/gpt-oss-20b` via Groq Cloud API for near-instant unhelpful bureaucratic replies.
- **PostgreSQL Persistence**: Automatically creates and syncs tables on startup:
  - `telemetry_metrics`: Tracks global chaos level, minutes wasted, and negative satisfaction.
  - `chat_logs`: Records all user interactions and bureaucratic handoffs.
  - `bureaucracy_submissions`: Logs Form 001 submissions and automatically stamps them with Catch-22 rejection codes.
- **Zero Frontend Disruption**: Built-in mock data for departments, quotes, captcha tiles, and vision samples so the frontend works even when offline.
- **Auto-healing Health Check**: Frontend polls `/api/health` to dynamically toggle live backend sync vs local storage fallback.

---

## Getting Started

### 1. Prerequisites
- Python 3.12+ (or `uv`)
- PostgreSQL 16+ running on `localhost:5432` with database `stupdt_db`

### 2. Environment Setup

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Ensure your credentials are set in `.env`:
```ini
ENVIRONMENT=development
PORT=8000
HOST=0.0.0.0
DATABASE_URL=postgresql+asyncpg://postgres@localhost:5432/stupdt_db
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
```

### 3. Install Dependencies
```bash
uv pip install --python .venv/bin/python -r requirements.txt
# Or standard pip:
pip install -r requirements.txt
```

### 4. Run the Dev Server
```bash
.venv/bin/uvicorn app.main:app --reload --port 8000
```
API Documentation (Interactive Swagger UI): **http://localhost:8000/docs**

---

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Service health status, database, and active AI model |
| `POST` | `/api/chat` | AI-powered bureaucratic chat (Groq / Gemini / Fallback) |
| `POST` | `/api/bureaucracy/submit` | Form 001 submission & Catch-22 simulator |
| `GET` | `/api/metrics` | Fetch current global bureaucratic telemetry |
| `POST` | `/api/metrics` | Synchronize metrics from frontend sessions |
| `GET` | `/api/departments` | Dynamic list of bureaucratic departments |
| `GET` | `/api/quotes` | Dynamic satirical corporate motivational quotes |
| `GET` | `/api/captcha` | Captcha tiles and legal math problems |
| `POST` | `/api/gemini` | Gemini proxy compatibility endpoint (Chat & Vision) |

---

## Testing

Run the test suite with `pytest`:
```bash
.venv/bin/pytest -v
```
