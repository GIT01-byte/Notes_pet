from uuid import UUID
from fastapi import UploadFile

from core.s3.s3_client import s3_client

from .constants import VIDEOS, IMAGES, AUDIO
from exceptions.exceptions import (
    FileInvalidCategoryError, 
    FileMaxSizeLimitError,
    ValidateFileFailedError,
)

from .media_repo import MediaRepo

from utils.logging import logger


# Сделать проверку целостности, простую проверку на вирусы, соответствие первичных байтов с помощью py_magic
class MediaService:
    async def _validate_file_category(self, file: UploadFile):
        try:
            logger.debug(f"Проверка категории файла {file.filename!r}, content-type: {file.content_type}")
            
            if not file.content_type:
                logger.warning(f"Отсутствует content-type для файла {file.filename!r}")
                return None

            if file.content_type in VIDEOS["content_types"]:
                logger.debug(f"Файл {file.filename!r} определен как video")
                return "video"
            elif file.content_type in IMAGES["content_types"]:
                logger.debug(f"Файл {file.filename!r} определен как image")
                return "image"
            elif file.content_type in AUDIO["content_types"]:
                logger.debug(f"Файл {file.filename!r} определен как audio")
                return "audio"
            else:
                logger.warning(f"Неизвестный content-type {file.content_type} для файла {file.filename!r}")
                return None
        except Exception as e:
            logger.exception(f"Ошибка валидации категории файла {file.filename!r}: {e}")
            return None

    async def _validate_file_size(self, file: UploadFile, category: str):
        try:
            logger.debug(f"Проверка размера файла {file.filename!r}, категория: {category}, размер: {file.size} байт")
            
            if not file.size:
                logger.warning(f"Отсутствует размер файла {file.filename!r}")
                return False

            if category == "video" and file.size <= VIDEOS["max_size"]:
                logger.debug(f"Размер video файла {file.filename!r} валиден")
                return True
            elif category == "image" and file.size <= IMAGES["max_size"]:
                logger.debug(f"Размер image файла {file.filename!r} валиден")
                return True
            elif category == "audio" and file.size <= AUDIO["max_size"]:
                logger.debug(f"Размер audio файла {file.filename!r} валиден")
                return True
            else:
                logger.warning(f"Размер файла {file.filename!r} превышает максимальный для категории {category}")
                return False
        except Exception as e:
            logger.exception(f"Ошибка валидации размера файла {file.filename!r}: {e}")
            return False

    async def validate_file(self, file: UploadFile):
        try:
            logger.info(f"Начало валидации файла {file.filename!r}")
            
            category = await self._validate_file_category(file)
            if category is None:
                logger.error(f"Файл {file.filename!r} не прошел валидацию категории")
                raise FileInvalidCategoryError
                
            if not await self._validate_file_size(file, category):
                logger.error(f"Файл {file.filename!r} не прошел валидацию размера")
                raise FileMaxSizeLimitError

            logger.info(f"Валидация файла {file.filename!r}, категории: {category!r} прошла успешно")
            return {
                "ok": True,
                "msg": f"Валидация файла: {file.filename!r}, категории: {category!r} прошла успешно",
            }
        except FileInvalidCategoryError:
            raise
        except FileMaxSizeLimitError:
            raise
        except Exception as e:
            logger.exception(f"Неожиданная ошибка валидации файла {file.filename!r}")
            raise ValidateFileFailedError from e
        