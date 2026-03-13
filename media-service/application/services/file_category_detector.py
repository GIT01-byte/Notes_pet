from fastapi import UploadFile
from pydantic import BaseModel, Field

from application.exceptions.base import BaseAPIException
from application.exceptions.exceptions import (
    EmptyFileError,
    FileCategoryNotSupportedError,
    ValidateFileFailedError,
)
from application.utils.constants import NOTES_ATTACHMENT_NAME, USERS_AVATAR_NAME
from application.utils.logging import logger


class FileCategory(BaseModel):
    name: str
    content_types: tuple[str, ...]
    extensions: tuple[str, ...]
    max_size: int = Field(gt=0)
    max_width: int | None = None
    max_height: int | None = None

    class Config:
        frozen = True


# Экземпляры категорий файлов
VIDEOS = FileCategory(
    name="video",
    content_types=(
        "video/mp4",
        "video/mpeg",
        "video/avi",
        "video/x-msvideo",
        "video/quicktime",
        "video/x-ms-wmv",
        "video/x-flv",
        "video/webm",
        "video/x-matroska",
    ),
    extensions=("mp4", "mpeg", "avi", "mov", "wmv", "flv", "webm", "mkv"),
    max_size=500 * 1024 * 1024,
    max_width=3160,
    max_height=3160,
)

IMAGES = FileCategory(
    name="image",
    content_types=(
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/bmp",
        "image/webp",
        "image/svg+xml",
        "image/x-icon",
        "image/vnd.microsoft.icon",
    ),
    extensions=("jpg", "jpeg", "png", "gif", "bmp", "webp", "svg", "ico"),
    max_size=30 * 1024 * 1024,
    max_width=3160,
    max_height=3160,
)

AUDIO = FileCategory(
    name="audio",
    content_types=("audio/mpeg", "audio/wav", "audio/wave", "application/ogg"),
    extensions=("mpeg", "mp3", "wav", "ogg"),
    max_size=30 * 1024 * 1024,
)

AVATARS = FileCategory(
    name="avatar",
    content_types=(
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/bmp",
        "image/webp",
        "image/svg+xml",
        "image/x-icon",
        "image/vnd.microsoft.icon",
    ),
    extensions=("jpg", "jpeg", "png", "gif", "bmp", "webp", "svg", "ico"),
    max_size=5 * 1024 * 1024,
    max_width=1024,
    max_height=1024,
)

# Маппинг для быстрого доступа
CATEGORIES_BY_NAME: dict[str, FileCategory] = {
    "video": VIDEOS,
    "image": IMAGES,
    "audio": AUDIO,
    "avatar": AVATARS,
}


class FileCategoryDetector:
    async def detect(self, file: UploadFile, upload_context: str) -> FileCategory:
        try:
            if not file or not file.content_type:
                raise EmptyFileError

            if (
                file.content_type in VIDEOS.content_types
                and upload_context == NOTES_ATTACHMENT_NAME
            ):
                return VIDEOS
            elif (
                file.content_type in IMAGES.content_types
                and upload_context == NOTES_ATTACHMENT_NAME
            ):
                return IMAGES
            elif (
                file.content_type in AUDIO.content_types
                and upload_context == NOTES_ATTACHMENT_NAME
            ):
                return AUDIO
            elif (
                file.content_type in AVATARS.content_types
                and upload_context == USERS_AVATAR_NAME
            ):
                return AVATARS
            else:
                raise FileCategoryNotSupportedError
        except BaseAPIException:
            raise
        except Exception as e:
            logger.exception(f"Ошибка определения категории файла: {e}")
            raise ValidateFileFailedError(
                detail=f"Failed to process file category for {file.filename}: {str(e)}"
            ) from e

    async def get_category_rules(self, category: str) -> FileCategory:
        category_obj = CATEGORIES_BY_NAME.get(category)
        if not category_obj:
            raise FileCategoryNotSupportedError
        return category_obj
