from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import RequestContextMiddleware
from app.core.exceptions import setup_exception_handlers
from app.modules.health.router import router as health_router
from app.modules.auth.router import router as auth_router
from app.modules.incidents.router import router as incidents_router
from app.modules.uploads.router import router as uploads_router

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

# Exception Handlers
setup_exception_handlers(app)

# Middleware
app.add_middleware(RequestContextMiddleware)

# Routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(incidents_router, prefix="/api/v1")
app.include_router(uploads_router, prefix="/api/v1")

