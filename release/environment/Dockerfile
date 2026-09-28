# Multi-stage production container for SciData Platform Research & API Runtime
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/platform/backend:/app

WORKDIR /app

# Install system dependencies for OpenCV, Pillow, and FAISS
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pinned Python dependencies
COPY requirements.txt requirements-lock.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy platform source and configuration
COPY configs/ /app/configs/
COPY src/ /app/src/
COPY platform/backend/ /app/platform/backend/
COPY pyproject.toml /app/

# Expose FastAPI port
EXPOSE 8000

CMD ["uvicorn", "platform.backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
