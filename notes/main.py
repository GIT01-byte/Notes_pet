from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from pydantic import ValidationError
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware

from api import router as api_router

from core.config import settings
from core.models import db_helper


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("INFO:     App is started")
    yield
    print('INFO:     Dispose db engine')
    await db_helper.dispose()


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
)

main_app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

main_app.include_router(
    api_router,
)


@main_app.middleware("http")
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
        "main:main_app",
        host=settings.app.host,
        port=settings.app.port,
        reload=True,
        log_level='debug'
    )
