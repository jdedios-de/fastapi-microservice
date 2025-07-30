from contextlib import asynccontextmanager
import time

import uvicorn
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import init_db
from app.instrumentation.tracing import init_tracer
from app.routers import protected_user, auth, protected_roles, protected_permissions
from app.utils.logger import get_logger

logger = get_logger("app.main")

@asynccontextmanager
async def lifespan(app_local: FastAPI):
    """Handle startup and shutdown events."""
    # Startup: Initialize database and tracing
    logger.info("Starting up application...")
    await init_db()
    init_tracer(app_local)
    logger.info("Database tables created and tracing initialized.")
    yield
    logger.info("Shutting down application...")

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests_and_add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    logger.info(
        "Handled %s request to %s with status %s from %s in %.2fs",
        request.method,
        request.url.path,
        response.status_code,
        request.client.host,
        process_time
    )
    response.headers["X-Process-Time"] = str(process_time)

    return response


app.include_router(protected_user.router, prefix="/api",tags=["User API"])
app.include_router(protected_roles.router, prefix="/api",tags=["Role API"])
app.include_router(protected_permissions.router, prefix="/api",tags=["Permission API"])
app.include_router(auth.router, tags=["Protected API Keys"])

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, log_level=settings.LOG_LEVEL)
