from uuid import UUID, uuid4
import clamd
from fastapi import UploadFile

from core.s3.s3_client import s3_client

from core.schemas.files import FileValidation
from .constants import VIDEOS, IMAGES, AUDIO
from exceptions.exceptions import (
    EmptyFileError,
    FileInvalidCategoryError,
    FileMaxSizeLimitError,
    FileVirusFoundError,
    InvalidFileCategoryError,
    ValidateFileFailedError,
    VirusScanFileFailedError,
)

from .media_repo import MediaRepo

from utils.logging import logger


class FileProcessingService:
    def __init__(self):
        self.metadata_handler = FileMetadataHandler()
        self.validator = FileContentValidator()
        self.generator_filename = GenerateUnigueFilename()
        self.virus_scanner = VirusScanner()

    async def process_file(self, file: UploadFile):
        # Проверка на наличие вирусов #FIXME
        # if not await self.virus_scanner.scan_for_viruses(file):
        #     raise VirusScanFileFailedError 

        # Получение категории файла
        category = await self.metadata_handler.get_file_category(file)
        if not category:
            raise ValidateFileFailedError(
                detail=f"Catagory handling error for file {file.filename!r}"
            )

        # Валидация файла
        if not await self.validator.validate_file(file, category):
            raise ValidateFileFailedError

        # Генерация уникального имени файла
        unigue_filename = await self.generator_filename.generate_unigue_filename(
            file, category
        )
        if not unigue_filename:
            raise ValidateFileFailedError(
                detail=f"Filename generation error for file {file.filename!r}"
            )

        return FileValidation(
            validaion_status=True,
            category=category,
            filename=unigue_filename,
        )


class FileMetadataHandler:
    async def get_file_category(self, file: UploadFile):
        try:
            logger.debug(
                f"Обработка категории файла {file.filename!r}, content-type: {file.content_type}"
            )

            if not file or not file.content_type:
                logger.warning("Попытка загрузки пустого файла")
                raise EmptyFileError

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
                logger.warning(
                    f"Неизвестный content-type {file.content_type} для файла {file.filename!r}"
                )
                raise InvalidFileCategoryError
        except EmptyFileError:
            raise
        except Exception as e:
            logger.exception(f"Ошибка обработки категории файла {file.filename!r}: {e}")
            raise ValidateFileFailedError(
                detail=f"Failed to process file category for {file.filename}: {str(e)}"
            ) from e


class GenerateUnigueFilename:
    async def generate_unigue_filename(self, file: UploadFile, category: str) -> str:
        try:
            logger.debug(f"Генерация нового имени файла для {file.filename!r}")

            if not file.filename or not category:
                logger.warning("Попытка генерации имени файла с пустыми параметрами")
                raise EmptyFileError(detail="Empty filename or category")

            uuid = str(uuid4())
            extension = file.filename.split(".")[-1].lower()

            if not extension:
                logger.warning(f"Файл {file.filename!r} не имеет расширения")
                raise EmptyFileError(detail=f"File {file.filename!r} has no extension")

            new_filename = f"{category}/{uuid}.{extension}"

            logger.info(
                f"Уникальное имя файла для {file.filename!r} сгенерировано: {new_filename}"
            )
            return new_filename
        except EmptyFileError:
            raise
        except Exception as e:
            logger.exception(
                f"Неожиданная ошибка генерации уникального имени файла {file.filename!r}: {e}"
            )
            raise ValidateFileFailedError(
                detail=f"Failed to generate unique filename for {file.filename}: {str(e)}"
            ) from e


# Сделать проверку целостности, соответствие первичных байтов с помощью py_magic, отчет о проведенной валидации файла
class FileContentValidator:
    async def _validate_file_size(self, file: UploadFile, category: str):
        try:
            logger.debug(
                f"Проверка размера файла {file.filename!r}, категория: {category}, размер: {file.size} байт"
            )

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
                logger.warning(
                    f"Размер файла {file.filename!r} превышает максимальный для категории {category}"
                )
                return False
        except Exception as e:
            logger.exception(f"Ошибка валидации размера файла {file.filename!r}: {e}")
            raise ValidateFileFailedError(
                detail=f"Failed to validate file size for {file.filename}: {str(e)}"
            ) from e

    async def validate_file(self, file: UploadFile, category: str):
        try:
            logger.info(f"Начало валидации файла {file.filename!r}")

            if not file.size or not category:
                logger.warning("Попытка загрузки пустого файла")
                raise EmptyFileError(detail="Empty file size or category")

            # Валидация размера файла
            if not await self._validate_file_size(file, category):
                logger.error(f"Файл {file.filename!r} не прошел валидацию размера")
                raise FileMaxSizeLimitError

            logger.info(
                f"Валидация файла {file.filename!r}, категории: {category!r} прошла успешно"
            )
            return True
        except EmptyFileError:
            raise
        except FileMaxSizeLimitError:
            raise
        except Exception as e:
            logger.exception(
                f"Неожиданная ошибка валидации файла {file.filename!r}: {e}"
            )
            raise ValidateFileFailedError(
                detail=f"Failed to validate file {file.filename}: {str(e)}"
            ) from e


class VirusScanner:
    def __init__(self):
        try:
            self.cd = clamd.ClamdUnixSocket()
            # Проверка соединения (пинг)
            self.cd.ping()
        except Exception as e:
            logger.error(f"Не удалось подключиться к ClamAV: {e}")
            self.cd = None

    async def scan_for_viruses(self, file: UploadFile):
        try:
            logger.debug(f"Сканирование файла {file.filename!r} на вирусы")

            if not file or not file.filename:
                raise EmptyFileError("Файл пуст или отсутствует имя")

            if self.cd is None:
                logger.error("Антивирусный сервис недоступен (self.cd is None)")
                raise VirusScanFileFailedError("ClamAV service is not initialized")

            # Читаем содержимое
            content = await file.read()

            # Сканируем буфер
            try:
                result = self.cd.instream(content)
            except Exception as e:
                logger.exception(f"Ошибка при передаче потока в ClamAV: {e}")
                raise VirusScanFileFailedError(f"Scan failed: {str(e)}")

            # Сбрасываем указатель, чтобы файл можно было прочитать снова (например, сохранить на диск)
            await file.seek(0)

            if not result or "stream" not in result:
                logger.error(
                    f"Некорректный ответ от ClamAV для файла {file.filename!r}"
                )
                raise VirusScanFileFailedError("Invalid response from scanner")

            # Если найдено 'FOUND', значит вирус есть
            status, virus_name = result.get("stream")
            if status == "FOUND":
                logger.info(f"ВИРУС ОБНАРУЖЕН: {virus_name} в файле {file.filename!r}")
                raise FileVirusFoundError(f"Virus {virus_name} found")

            logger.info(f"Файл {file.filename!r} чист")
            return True

        except (EmptyFileError, FileVirusFoundError, VirusScanFileFailedError):
            raise
        except Exception as e:
            logger.exception(f"Непредвиденная ошибка при сканировании: {e}")
            raise VirusScanFileFailedError(detail=f"Internal error: {str(e)}")
