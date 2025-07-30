from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from fastapi import FastAPI
from app.config import settings

def init_tracer(app: FastAPI) -> None:
    """Initialize OpenTelemetry tracing for the FastAPI app."""
    # Set up the TracerProvider
    trace.set_tracer_provider(TracerProvider())

    # Configure OTLP exporter
    otlp_exporter = OTLPSpanExporter(
        endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
        insecure=True,  # Set to False in production with TLS
    )

    # Add BatchSpanProcessor to export spans
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

    # Instrument FastAPI to automatically trace requests
    FastAPIInstrumentor.instrument_app(app)

async def get_tracers():
    return trace.get_tracer("app.instrumentation.tracing")
