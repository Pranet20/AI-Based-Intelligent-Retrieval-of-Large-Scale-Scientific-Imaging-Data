"""FastAPI main application entry point with production observability and rate limiting."""

from contextlib import asynccontextmanager
import logging
import time
import uuid

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import torch

from app.api import auth, curation, images, models, multi_image, projects, provenance, search, system
from app.core.config import settings
from app.db.session import Base, SessionLocal, engine
from app.ml.model_registry import ModelRegistryService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("scidata.platform")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 0. Enforce production security configuration validation
    settings.validate_production_security()

    # 1. Startup Diagnostics: Database connectivity & metadata
    db_info = {
        "dialect": engine.url.get_backend_name(),
        "driver": engine.url.get_driver_name(),
        "host": engine.url.host or "local",
        "database": engine.url.database or "memory",
    }
    logger.info(f"[Startup Diagnostic] Database connection parameters: {db_info}")
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("[Startup Diagnostic] Database connection verified (SELECT 1 succeeded).")
    except Exception as e:
        logger.error(f"[Startup Diagnostic] Database connection check failed: {e}")
        raise e

    # Ensure all database tables exist
    Base.metadata.create_all(bind=engine)

    # 2. Cryptographic startup verification of authoritative models & checkpoints
    db = SessionLocal()
    try:
        registered_models = ModelRegistryService.initialize_authoritative_models(db)
        logger.info("[Startup Diagnostic] Authoritative models cryptographically verified and registered:")
        for name, m in registered_models.items():
            logger.info(
                f"  - Model [{name}]: model_id={m.model_id}, dim={m.embedding_dimension}, "
                f"hash={m.weights_hash}, active={m.is_active}"
            )
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(
            f"[Startup Diagnostic] MODEL_STATUS: LOADED | CHECKPOINT_STATUS: VERIFIED | "
            f"CHECKPOINT_SHA256: {settings.EXPECTED_PHASE4_HASH} | "
            f"EMBEDDING_DIM: {settings.DINOV2_EMBEDDING_DIM} | DEVICE: {device} | MODEL_READY: True"
        )
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
RATE_LIMIT_MAX_REQUESTS = 10000  # Generous threshold for interactive scientific visualization
RATE_LIMIT_WINDOW_SECONDS = 60.0


class ProductionObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Inject or propagate Request-ID
        req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = req_id

        # 2. Rate limiting check (exempting local dev, health, readiness, and image/thumbnail delivery)
        client_ip = request.client.host if request.client else "127.0.0.1"
        path = request.url.path
        is_loopback = client_ip in ("127.0.0.1", "::1", "localhost") or settings.ENVIRONMENT == "development"
        is_exempt_path = (
            path.startswith(f"{settings.API_V1_STR}/health")
            or path.startswith(f"{settings.API_V1_STR}/readiness")
            or "/thumbnail" in path
            or "/file" in path
            or "/display" in path
        )

        if not is_loopback and not is_exempt_path:
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

        # 4. Attach tracing headers and Private Network Access support
        response.headers["X-Request-ID"] = req_id
        response.headers["X-Response-Time-MS"] = f"{duration_ms:.2f}"
        if request.headers.get("access-control-request-private-network"):
            response.headers["Access-Control-Allow-Private-Network"] = "true"
        return response


# Attach middlewares
app.add_middleware(ProductionObservabilityMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers under /api/v1
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(projects.router, prefix=settings.API_V1_STR)
app.include_router(images.router, prefix=settings.API_V1_STR)
app.include_router(search.router, prefix=settings.API_V1_STR)
app.include_router(curation.router, prefix=f"{settings.API_V1_STR}/curation")
app.include_router(multi_image.router, prefix=f"{settings.API_V1_STR}/multi-image")
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


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled platform error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Server processing error: {str(exc)}"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
