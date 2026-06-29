import uuid
from typing import Callable, Awaitable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import structlog
from datetime import datetime
import time
from app.core.exceptions import SOCCopilotError

logger = structlog.get_logger(__name__)

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        request_id = str(uuid.uuid4())
        structlog.contextvars.bind_contextvars(request_id=request_id)
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log the request completion
            logger.info("request.completed", 
                        method=request.method, 
                        path=request.url.path, 
                        status_code=response.status_code, 
                        duration_ms=duration_ms)
            
            response.headers["X-Request-ID"] = request_id
            return response
            
        except SOCCopilotError as e:
            # Handle specific known exceptions
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error("request.failed", 
                         method=request.method, 
                         path=request.url.path, 
                         error=str(e), 
                         duration_ms=duration_ms)
                         
            return JSONResponse(
                status_code=400, # Should map based on exception type later
                content={
                    "error": e.__class__.__name__,
                    "message": str(e),
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            )
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.exception("request.unhandled_exception", 
                             method=request.method, 
                             path=request.url.path, 
                             duration_ms=duration_ms)
                             
            return JSONResponse(
                status_code=500,
                content={
                    "error": "internal_server_error",
                    "message": "An unexpected error occurred.",
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            )
