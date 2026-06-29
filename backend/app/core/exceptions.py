from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.shared.schemas import APIErrorResponse, ErrorDetail

class SOCCopilotError(Exception):
    """Base exception for all SOC Copilot errors."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

class NotFoundError(SOCCopilotError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, code="NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)

class PermissionDeniedError(SOCCopilotError):
    """Raised when user does not have required permissions."""
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, code="PERMISSION_DENIED", status_code=status.HTTP_403_FORBIDDEN)

class LLMUnavailableError(SOCCopilotError):
    """Raised when an LLM provider is unavailable or fails."""
    def __init__(self, message: str = "LLM Provider Unavailable"):
        super().__init__(message, code="LLM_UNAVAILABLE", status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

class UnauthenticatedError(SOCCopilotError):
    def __init__(self, message: str = "Not authenticated"):
        super().__init__(message, code="UNAUTHENTICATED", status_code=status.HTTP_401_UNAUTHORIZED)

class ValidationError(SOCCopilotError):
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, code="VALIDATION_ERROR", status_code=status.HTTP_400_BAD_REQUEST)

class ConflictError(SOCCopilotError):
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, code="CONFLICT", status_code=status.HTTP_409_CONFLICT)

def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(SOCCopilotError)
    async def soc_copilot_exception_handler(request: Request, exc: SOCCopilotError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=APIErrorResponse(
                success=False,
                error=ErrorDetail(code=exc.code, message=exc.message)
            ).model_dump()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=APIErrorResponse(
                success=False,
                error=ErrorDetail(
                    code="VALIDATION_ERROR",
                    message="Request validation failed",
                    details=exc.errors()
                )
            ).model_dump()
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        import structlog
        logger = structlog.get_logger()
        logger.exception("Unhandled exception", exc=str(exc))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=APIErrorResponse(
                success=False,
                error=ErrorDetail(code="INTERNAL_ERROR", message="An unexpected error occurred.")
            ).model_dump()
        )
