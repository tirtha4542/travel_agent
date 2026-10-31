# ✈️ TreapMate AI — Autonomous Travel Companion

TreapMate AI is an autonomous multi-agent travel planning system built with **FastAPI**, **LangGraph**, **Groq (GPT-OSS/LLaMA)**, **AviationStack**, and **Tavily**. It automatically identifies your hub, retrieves live flights with real-time verification links, locates top-rated hotels, and compiles practical, day-by-day travel itineraries.

---

## 🚀 Quick Start (Local)

### 1. Prerequisites
- Python 3.12+ (or 3.13)
- Virtual environment (`venv` or `uv`)

### 2. Environment Setup
Copy the example environment configuration:
```bash
cp .env.example .env
```
Fill in your API keys in `.env`:
- `GROQ_API_KEY`: Groq API key for LLM agents
- `AVIATION_STACK_API_KEY`: Real-time flight tracking
- `TAVILY_API_KEY`: Real-time web search for hotels and route insights
- `DATABASE_URL`: PostgreSQL connection string (optional; defaults to in-memory checkpointer)

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```
Open your browser at **`http://localhost:8000`**.

---

## 🐳 Running with Docker

### Option A: Using Docker Compose (Recommended)
Make sure your `.env` file is configured, then run:
```bash
docker compose up --build -d
```
To view logs:
```bash
docker compose logs -f
```
To stop the container:
```bash
docker compose down
```

### Option B: Using Docker CLI Directly
1. **Build the Docker Image:**
   ```bash
   docker build -t treapmate-ai .
   ```

2. **Run the Container:**
   ```bash
   docker run -d \
     --name treapmate_app \
     -p 8000:8000 \
     --env-file .env \
     treapmate-ai
   ```

Open your browser at **`http://localhost:8000`**.

---

## 📂 Project Structure
```text
├── app/
│   ├── agent/               # Multi-agent LangGraph workflows & nodes
│   │   ├── tools/           # AviationStack flight & Tavily search tools
│   │   ├── graph.py         # StateGraph compiled execution pipeline
│   │   ├── nodes.py         # Specialized agent node definitions
│   │   ├── prompts.py       # Anti-hallucination prompts & formatting
│   │   └── state.py         # TypedDict state schema
│   ├── core/                # Database and application configuration
│   ├── routes/              # FastAPI endpoints (chat API & HTML view)
│   └── main.py              # FastAPI application factory
├── static/                  # Responsive CSS, JavaScript controller & SVG favicon
├── templates/               # Single-page UI workspace (index.html)
├── Dockerfile               # Production multi-stage Docker container
├── docker-compose.yml       # Docker Compose service definition
├── .dockerignore            # Excludes virtual environments and secrets
├── requirements.txt         # Clean production dependencies
└── app.py                   # Root entrypoint
```

---

## 🛡️ License
MIT License.

