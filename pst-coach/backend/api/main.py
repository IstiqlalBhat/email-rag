"""
Main FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_client import make_asgi_app

from core.config import settings
from core.logging import setup_logging
from api.routes import auth, uploads, jobs, mailboxes, chat, privacy
from api.middleware.error_handler import ErrorHandlerMiddleware
from api.middleware.request_id import RequestIDMiddleware
from api.middleware.tenant import TenantMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    setup_logging()
    yield
    # Shutdown
    pass


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Email Intelligence & Self-Reflection Platform",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(TenantMiddleware)

# Mount Prometheus metrics
if settings.PROMETHEUS_ENABLED:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

# API Routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(uploads.router, prefix="/api/uploads", tags=["Uploads"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(mailboxes.router, prefix="/api/mailboxes", tags=["Mailboxes"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(privacy.router, prefix="/api/privacy", tags=["Privacy"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
