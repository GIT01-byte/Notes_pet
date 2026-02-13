from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from pydantic import ValidationError
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware

from api import router as api_router

from core.config import settings

from utils.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("App is started")
    yield
    logger.info('App is turn off')


# Middleware для логирования ошибок
class ExceptionLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except ValidationError as e:
            print(f"EXC:   Validation Error: {e.errors()}")
            raise  # Re-raise the exception to be handled by FastAPI's default exception handlers
        except Exception as e:
            print(f"EXC:   Unhandled Exception: {e}")
            raise  # Re-raise the exception


middleware = [
    Middleware(ExceptionLoggingMiddleware)
]


main_app = FastAPI(
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    middleware=middleware,
)


origins = [
    "http://127.0.0.1",
]


main_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


main_app.include_router(api_router)


@main_app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"\n----------- New request -----------")
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Headers: {request.headers}")
    try:
        body = await request.json()
        logger.info(f"Body: {body}\n")
    except Exception as e:
        logger.warning(f"Could not decode JSON body: {e}\n")
    response = await call_next(request)
    return response
 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:main_app",
        host=settings.app.host,
        port=settings.app.port,
        reload=True,
        log_level='debug'
    )
