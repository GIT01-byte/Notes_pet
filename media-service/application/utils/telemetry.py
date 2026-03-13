from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def setup_telemetry(app, service_name: str = "fastapi-app"):
    """Инициализация OpenTelemetry с экспортом в OTLP (Jaeger/Tempo)."""

    resource = Resource.create(
        {
            SERVICE_NAME: service_name,
            SERVICE_VERSION: "1.0.0",
            "deployment.environment": "production",
        }
    )

    # TracerProvider — центральный объект для создания трейсов
    provider = TracerProvider(resource=resource)

    # Экспорт через OTLP (gRPC) — универсальный протокол
    otlp_exporter = OTLPSpanExporter(
        endpoint="http://jaeger:4317",  # или Tempo, или OTel Collector
        insecure=True,
    )

    # BatchSpanProcessor — буферизация и отправка пачками
    provider.add_span_processor(
        BatchSpanProcessor(
            otlp_exporter,
            max_queue_size=2048,
            max_export_batch_size=512,
            schedule_delay_millis=5000,
        )
    )

    trace.set_tracer_provider(provider)

    # Автоматическая инструментация
    FastAPIInstrumentor.instrument_app(app)
    # HTTPXClientInstrumentor().instrument()  # httpx — async HTTP клиент
    SQLAlchemyInstrumentor().instrument()  # SQLAlchemy queries
    # RedisInstrumentor().instrument()  # Redis commands
