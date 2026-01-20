from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from debug_toolbar.middleware import DebugToolbarMiddleware

from api import router as api_router

from core.config import settings
from core.models import db_helper


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("INFO:     App is started")
    yield
    print('INFO:     Dispose db engine')
    await db_helper.dispose()


main_app = FastAPI(
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

main_app.add_middleware(
    CORSMiddleware,
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
    # Получаем body (только для чтения)
    response = await call_next(request)
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:main_app",
        host=settings.app.host,
        port=settings.app.port,
        reload=True
    )
