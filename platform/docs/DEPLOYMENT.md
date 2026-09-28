# Production Deployment Specification

## 1. Quick Start via Docker Compose
To deploy the full production platform including PostgreSQL, FastAPI backend, and Nginx frontend:

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Build and launch services in detached mode
docker-compose up -d --build

# 3. Check container status
docker-compose ps

# 4. View backend logs
docker-compose logs -f backend
```

- **Frontend UI**: http://localhost:3000
- **REST API & Swagger Docs**: http://localhost:8000/docs
- **PostgreSQL Database**: localhost:5432 (Database: `scidata_platform`)

## 2. Local Bare-Metal Development

### Backend
```bash
# Activate virtual environment
source .venv311/bin/activate  # or .venv311\Scripts\activate on Windows

# Set Python path
export PYTHONPATH="platform/backend:."

# Launch FastAPI development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend
```bash
cd platform/frontend
npm install
npm start
```
