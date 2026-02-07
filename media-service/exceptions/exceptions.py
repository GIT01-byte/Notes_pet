from fastapi import status
from .base import BaseAPIException, RepositoryError


# --- Базовые исключения Репозитория ---
class RepositoryInternalError(RepositoryError):
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(detail=detail)


class EntityNotFoundError(BaseAPIException):
    def __init__(self, detail: str = "Entity not found"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class DataConflictError(BaseAPIException):
    def __init__(self, detail: str = "Data conflict occurred"):
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)


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


class FileMetadataAlreadyExistsError(BaseAPIException):
    def __init__(self, detail: str = "File metadata already exists"):
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)
