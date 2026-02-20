import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

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
# Исключения кук
class UserCookieMissingError(BaseAPIException):
    def __init__(self, detail: str = "Missing required cookies for login user"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


# Исключения обработчиков данных заметок
class DeleteNoteError(BaseAPIException):
    def __init__(self, detail: str = "Note is not delete"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class NoteAlreadyExistsError(BaseAPIException):
    def __init__(self, detail: str = "Note already exists"):
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)


class NoteNotFoundError(BaseAPIException):
    def __init__(self, detail: str = "Note(s) not found"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


# Исключения обработки файлов
class EmptyFileError(BaseAPIException):
    def __init__(self, detail: str = "File is empty"):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class FilesHandlingError(BaseAPIException):
    def __init__(self, detail: str = "Error handling files"):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class InvalidFileFormatError(BaseAPIException):
    def __init__(self, detail: str = "Invalid file format"):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class FilesUploadError(BaseAPIException):
    def __init__(self, detail: str = "Error uploading files"):
        super().__init__(
            detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class FilesDeleteError(BaseAPIException):
    def __init__(self, detail: str = "Error deleting files"):
        super().__init__(
            detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Исключения сервисов о проваленной работе
class NoteCreateFailedError(BaseAPIException):
    def __init__(self, detail: str = "Note create failed"):
        super().__init__(
            detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class NoteDeleteFailedError(BaseAPIException):
    def __init__(self, detail: str = "Note delete failed"):
        super().__init__(
            detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class NoteSelectFailedError(BaseAPIException):
    def __init__(self, detail: str = "Note select failed"):
        super().__init__(
            detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Исключения redis
# class RedisConnectionError(BaseAPIException):
#     def __init__(self, detail: str = "Failed to connect Redis due to internal error"):
#         super().__init__(
#             detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )
