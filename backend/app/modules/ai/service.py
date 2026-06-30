import logging
from typing import Type, Optional, AsyncGenerator
from pydantic import BaseModel

from app.modules.ai.provider import provider_registry

logger = logging.getLogger(__name__)

class LLMService:
    """
    Public Interface for all AI Modules. 
    Handles retries, validation logic, and provider resolution.
    """
    def __init__(self, provider_name: Optional[str] = None):
        self.provider = provider_registry.get_provider(provider_name)
        
    async def analyze_structured(self, prompt: str, schema: Type[BaseModel], model: str = "default", max_retries: int = 1) -> BaseModel:
        """
        Requests a structured response. If validation fails, it retries once with repair instructions.
        """
        last_exception = None
        current_prompt = prompt
        
        for attempt in range(max_retries + 1):
            try:
                # Add instructions for JSON output schema if it's the first attempt
                if attempt == 0:
                    schema_json = schema.model_json_schema()
                    current_prompt += f"\n\nYou MUST return a JSON object adhering exactly to this schema:\n{schema_json}"
                    
                result = await self.provider.generate_structured(current_prompt, schema, model)
                return result
                
            except ValueError as e:
                logger.warning(f"Attempt {attempt + 1} structured generation failed: {e}")
                last_exception = e
                # Prepare repair prompt for next iteration
                current_prompt = prompt + f"\n\nYOUR PREVIOUS RESPONSE FAILED VALIDATION WITH ERROR: {str(e)}\n\nPlease try again and ensure the output is valid JSON matching the schema."
                
        # If we exhausted retries, throw a structured error or raise
        logger.error(f"Failed to generate structured output after {max_retries + 1} attempts.")
        raise last_exception

    async def chat_stream(self, prompt: str, model: str = "default") -> AsyncGenerator[str, None]:
        """
        Stream chat responses.
        """
        async for chunk in self.provider.generate_stream(prompt, model):
            yield chunk
