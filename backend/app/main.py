from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import RequestContextMiddleware
from app.modules.health.router import router as health_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging(settings.APP_ENV)
    yield
    # Shutdown

app = FastAPI(
    title="SOC Copilot API",
    version="0.1.0",
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(RequestContextMiddleware)

# Routers
app.include_router(health_router)

