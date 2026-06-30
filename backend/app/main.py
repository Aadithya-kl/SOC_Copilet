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
from app.modules.investigation.router import router as investigations_router
from app.modules.mitre.router import router as mitre_router
from app.modules.evidence.router import router as evidence_router
from app.modules.correlation.router import router as correlation_router
from app.modules.graph.router import router as graph_router
from app.modules.timeline.router import router as timeline_router
from app.modules.ai.router import router as ai_router

from prometheus_fastapi_instrumentator import Instrumentator
from app.core.telemetry import setup_telemetry
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging(settings.APP_ENV)
    logger.info("Starting SOC Copilot Backend...")
    setup_telemetry(app)
    Instrumentator().instrument(app).expose(app, include_in_schema=True)
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

from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import Request, status

class MaxSizeMiddleware:
    def __init__(self, app, max_upload_size: int = 100 * 1024 * 1024): # 100MB
        self.app = app
        self.max_upload_size = max_upload_size

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
            
        request = Request(scope, receive)
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_upload_size:
            response = JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"detail": "Payload too large"}
            )
            return await response(scope, receive, send)
            
        await self.app(scope, receive, send)

# Middleware
app.add_middleware(MaxSizeMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"]) # In production this would be restricted
app.add_middleware(RequestContextMiddleware)

# Routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(incidents_router, prefix="/api/v1")
app.include_router(uploads_router, prefix="/api/v1")
app.include_router(investigations_router, prefix="/api/v1")
app.include_router(mitre_router, prefix="/api/v1")
app.include_router(evidence_router, prefix="/api/v1")
app.include_router(correlation_router, prefix="/api/v1")
app.include_router(graph_router, prefix="/api/v1")
app.include_router(timeline_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")

