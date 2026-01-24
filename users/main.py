import os
import sys

from pydantic import ValidationError
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from core.settings import settings
from core.models.user_admin import setup_admin
from core.db.db_manager import db_manager
from api import api_routers

from utils.logging import logger

import tracemalloc

from prometheus_fastapi_instrumentator import Instrumentator

# Включаем отслеживание памяти, для дебага ошибок с ассинхронными функциями
tracemalloc.start()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Запуск приложения...')
    yield
    logger.info('Выключение...')


# Middleware для логирования ошибок
class ExceptionLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except ValidationError as e:
            logger.error(f"Validation Error: {e.errors()}")
            raise  # Re-raise the exception to be handled by FastAPI's default exception handlers
        except Exception as e:
            logger.exception(f"Unhandled Exception: {e}")
            raise  # Re-raise the exception


middleware = [
    Middleware(ExceptionLoggingMiddleware)
]

app = FastAPI(
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    middleware=middleware,
)


origins = [
    "http://127.0.0.1:5500",
    "http://localhost:8080",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем api роутеры
app.include_router(api_routers)

# Подключаем prometheus метрики
Instrumentator().instrument(app).expose(app)

# Подключаем админ панель
# setup_admin(app, db_manager.engine)

# Подключаем middleware для просмотра содержимого http запроса
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"INFO:    Request: {request.method} {request.url}")
    print(f"INFO:    Headers: {request.headers}")
    try:
        body = await request.json()
        print(f"INFO:    Body: {body}")
    except Exception as e:
        print(f"WARNING: Could not decode JSON body: {e}")
    response = await call_next(request)
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=True,
        log_level='debug'
    )