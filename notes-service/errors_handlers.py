from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError

from utils.logging import logger


def register_errors_handlers(app: FastAPI) -> None:
    @app.exception_handler(ValidationError)
    async def handle_pydantic_validation_errors(
        request: Request,
        exc: ValidationError,
    ):
        logger.error(f"Validation error: {exc.errors()}")
        return ORJSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "message": "Unhandled error",
                "error": exc.errors(),
            },
        )
