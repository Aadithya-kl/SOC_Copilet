import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from fastapi import FastAPI

logger = logging.getLogger(__name__)

def setup_telemetry(app: FastAPI):
    # Set up TracerProvider
    provider = TracerProvider()
    
    # In a real production setup, we would export to Jaeger or OTLP.
    # For now, we use a Console exporter or just rely on context propagation for logs.
    # processor = BatchSpanProcessor(ConsoleSpanExporter())
    # provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)

    # Instrument other libraries (SQLAlchemy engine instrumentation is typically done when engine is created)
    # Redis and HTTPX can be instrumented globally
    RedisInstrumentor().instrument()
    HTTPXClientInstrumentor().instrument()
    
    logger.info("OpenTelemetry instrumentation completed.")
