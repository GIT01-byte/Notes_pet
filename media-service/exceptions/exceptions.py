from fastapi import status
from .base import BaseAPIException


# --- Базовые исключения API ---
class BaseFileHandlerError(BaseAPIException):
    def __init__(self, detail: str = "Error handling files"):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)