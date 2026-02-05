from fastapi import status
from .base import BaseAPIException


# --- Базовые исключения API ---
class FilesHandlingError(BaseAPIException):
    def __init__(self, detail: str = "Error handling files"):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class FilesUploadError(BaseAPIException):
    def __init__(self, detail: str = "Error uploading files"):
        super().__init__(
            detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class InvalidFileFormatError(BaseAPIException):
    def __init__(self, detail: str = "Invalid file format"):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)
