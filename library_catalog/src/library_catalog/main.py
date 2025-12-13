# src/library_catalog/main.py
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.logging_config import setup_logging
from .core.database import dispose_engine
from .core.clients import clients_manager
from .core.exceptions import register_exception_handlers
from .api.v1.routers import books, health

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("🚀 Application started")

    try:
        yield
    finally:
        logger.info("👋 Application stopping...")
        try:
            await clients_manager.close_all()
            logger.info("Clients closed")
        except Exception:
            logger.exception("Failed to close clients")

        try:
            await dispose_engine()
            logger.info("DB engine disposed")
        except Exception:
            logger.exception("Failed to dispose DB engine")

        logger.info("✅ Application stopped")


app = FastAPI(
    title=settings.app_name,
    description="REST API для управления библиотечным каталогом",
    version="1.0.0",
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(books.router, prefix=settings.api_v1_prefix)
app.include_router(health.router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    return {"message": "Welcome to Library Catalog API", "docs": settings.docs_url, "version": "1.0.0"}
