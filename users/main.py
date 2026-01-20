import os
import sys

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

app = FastAPI(
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем api роутеры
app.include_router(api_routers)

# Подключаем prometheus метрики
Instrumentator().instrument(app).expose(app)

# # Подключаем админ панель
# setup_admin(app, db_manager.engine)

# # Подключаем middleware для просмотра содержимого http запроса
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"INFO:    Request: {request.method} {request.url}")
    print(f"INFO:    Headers: {request.headers}")
    # Получаем body (только для чтения)
    response = await call_next(request)
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=True
    )