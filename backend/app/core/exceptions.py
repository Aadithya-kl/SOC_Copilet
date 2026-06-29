class SOCCopilotError(Exception):
    """Base exception for all SOC Copilot errors."""
    pass

class NotFoundError(SOCCopilotError):
    pass

class PermissionDeniedError(SOCCopilotError):
    pass

class ValidationError(SOCCopilotError):
    pass

class ConflictError(SOCCopilotError):
    pass

class RateLimitError(SOCCopilotError):
    pass

class ExternalServiceError(SOCCopilotError):
    pass

class LLMUnavailableError(ExternalServiceError):
    pass

class TIProviderError(ExternalServiceError):
    pass

class StorageError(ExternalServiceError):
    pass

class PipelineError(SOCCopilotError):
    pass

class AgentError(PipelineError):
    pass

class ParseError(PipelineError):
    pass
