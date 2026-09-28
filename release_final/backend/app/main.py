"""FastAPI main application entry point with production observability and rate limiting."""

from contextlib import asynccontextmanager
import time
import uuid

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.api import auth, curation, images, models, projects, provenance, search, system
from app.core.config import settings
from app.db.session import Base, SessionLocal, engine
from app.ml.model_registry import ModelRegistryService


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Ensure all database tables exist
    Base.metadata.create_all(bind=engine)

    # 2. Cryptographic startup verification of authoritative models
    db = SessionLocal()
    try:
        ModelRegistryService.initialize_authoritative_models(db)
        print("Authoritative models cryptographically verified and registered.")
    finally:
        db.close()

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production Research Platform for AI-Powered Scientific Image Data Management",
    lifespan=lifespan,
)

# In-memory rate limiting state: client_ip -> [timestamps]
_RATE_LIMIT_STORE = {}
RATE_LIMIT_MAX_REQUESTS = 300  # per minute
RATE_LIMIT_WINDOW_SECONDS = 60.0


class ProductionObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Inject or propagate Request-ID
        req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = req_id

        # 2. Rate limiting check (excluding health and readiness checks)
        client_ip = request.client.host if request.client else "127.0.0.1"
        path = request.url.path
        if not path.startswith(f"{settings.API_V1_STR}/health") and not path.startswith(f"{settings.API_V1_STR}/readiness"):
            now = time.time()
            timestamps = _RATE_LIMIT_STORE.get(client_ip, [])
            timestamps = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW_SECONDS]
            if len(timestamps) >= RATE_LIMIT_MAX_REQUESTS:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too Many Requests", "request_id": req_id},
                    headers={"X-Request-ID": req_id, "Retry-After": "60"},
                )
            timestamps.append(now)
            _RATE_LIMIT_STORE[client_ip] = timestamps

        # 3. Process request and measure latency
        start_time = time.perf_counter()
        response: Response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000.0

        # 4. Attach tracing headers
        response.headers["X-Request-ID"] = req_id
        response.headers["X-Response-Time-MS"] = f"{duration_ms:.2f}"
        return response


# Attach middlewares
app.add_middleware(ProductionObservabilityMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers under /api/v1
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(projects.router, prefix=settings.API_V1_STR)
app.include_router(images.router, prefix=settings.API_V1_STR)
app.include_router(search.router, prefix=settings.API_V1_STR)
app.include_router(curation.router, prefix=settings.API_V1_STR)
app.include_router(curation.router, prefix=f"{settings.API_V1_STR}/curation")
app.include_router(models.router, prefix=settings.API_V1_STR)
app.include_router(provenance.router, prefix=settings.API_V1_STR)
app.include_router(system.router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "api": f"{settings.API_V1_STR}/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
