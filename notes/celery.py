from celery import Celery


celery_app = Celery(
    "fastapi-app.celery",
    broker="amqp://guest:guest@localhost:5672//",
    backend="rpc://",
)
