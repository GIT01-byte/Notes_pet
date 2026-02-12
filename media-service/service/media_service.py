from uuid import UUID, uuid4
import pyclamd
from fastapi import UploadFile

from core.s3.s3_client import s3_client

from core.schemas.files import FileValidation
from .constants import VIDEOS, IMAGES, AUDIO
from exceptions.exceptions import (
    EmptyFileError,
    FileCategoryNotSupportedError,
    FileMaxSizeLimitError,
    FileVirusFound,
    ProcessFileFailedError,
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
        try:
            logger.info(f"Обработка файла {file.filename!r}")

            if not file or not file.filename:
                logger.warning("Попытка загрузки пустого файла")
                raise EmptyFileError

            # Проверка на наличие вирусов
            if not await self.virus_scanner.scan_for_viruses(file):
                raise VirusScanFileFailedError

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

            logger.info(f"File {file.filename!r} successfully processed")
            return FileValidation(
                validaion_status=True,
                category=category,
                filename=unigue_filename,
            )
        except (
            EmptyFileError,
            FileCategoryNotSupportedError,
            FileMaxSizeLimitError,
            FileVirusFound,
            ValidateFileFailedError,
            VirusScanFileFailedError,
        ):
            raise
        except Exception as e:
            logger.exception(f"Failed to process file {file.filename!r}: {e}")
            raise ProcessFileFailedError(
                detail=f"Failed to process file {file.filename}: {str(e)}"
            ) from e


class FileMetadataHandler:
    async def get_file_category(self, file: UploadFile):
        try:
            logger.debug(
                f"Processing file category {file.filename!r}, content-type: {file.content_type}"
            )

            if not file or not file.content_type:
                logger.warning("Attempt to upload empty file")
                raise EmptyFileError

            if file.content_type in VIDEOS["content_types"]:
                logger.debug(f"File {file.filename!r} identified as video")
                return "video"
            elif file.content_type in IMAGES["content_types"]:
                logger.debug(f"File {file.filename!r} identified as image")
                return "image"
            elif file.content_type in AUDIO["content_types"]:
                logger.debug(f"File {file.filename!r} identified as audio")
                return "audio"
            else:
                logger.warning(
                    f"Unknown content-type {file.content_type} for file {file.filename!r}"
                )
                raise FileCategoryNotSupportedError
        except (EmptyFileError, FileCategoryNotSupportedError):
            raise
        except Exception as e:
            logger.exception(f"Failed to process file category {file.filename!r}: {e}")
            raise ValidateFileFailedError(
                detail=f"Failed to process file category for {file.filename}: {str(e)}"
            ) from e


class GenerateUnigueFilename:
    async def generate_unigue_filename(self, file: UploadFile, category: str) -> str:
        try:
            logger.debug(f"Generating unique filename for {file.filename!r}")

            if not file.filename or not category:
                logger.warning("Attempt to generate filename with empty parameters")
                raise EmptyFileError(detail="Empty filename or category")

            uuid = str(uuid4())
            extension = file.filename.split(".")[-1].lower()

            if not extension:
                logger.warning(f"File {file.filename!r} has no extension")
                raise EmptyFileError(detail=f"File {file.filename!r} has no extension")

            new_filename = f"{category}/{uuid}.{extension}"

            logger.info(
                f"Unique filename for {file.filename!r} generated: {new_filename}"
            )
            return new_filename
        except EmptyFileError:
            raise
        except Exception as e:
            logger.exception(
                f"Failed to generate unique filename for {file.filename!r}: {e}"
            )
            raise ValidateFileFailedError(
                detail=f"Failed to generate unique filename for {file.filename}: {str(e)}"
            ) from e


class FileContentValidator:
    async def _validate_file_size(self, file: UploadFile, category: str):
        try:
            logger.debug(
                f"Validating file size {file.filename!r}, category: {category}, size: {file.size} bytes"
            )

            if not file or not file.size:
                logger.warning("Attempt to validate empty file size")
                raise EmptyFileError(detail="Empty file size")

            if category == "video" and file.size <= VIDEOS["max_size"]:
                logger.debug(f"Video file {file.filename!r} size is valid")
                return True
            elif category == "image" and file.size <= IMAGES["max_size"]:
                logger.debug(f"Image file {file.filename!r} size is valid")
                return True
            elif category == "audio" and file.size <= AUDIO["max_size"]:
                logger.debug(f"Audio file {file.filename!r} size is valid")
                return True
            else:
                logger.warning(
                    f"File {file.filename!r} size exceeds maximum for category {category}"
                )
                return False
        except EmptyFileError:
            raise
        except Exception as e:
            logger.exception(f"Failed to validate file size {file.filename!r}: {e}")
            raise ValidateFileFailedError(
                detail=f"Failed to validate file size for {file.filename}: {str(e)}"
            ) from e

    async def validate_file(self, file: UploadFile, category: str):
        try:
            if not file.size or not category:
                logger.warning("Attempt to validate empty file")
                raise EmptyFileError(detail="Empty file size or category")

            if not await self._validate_file_size(file, category):
                logger.error(f"File {file.filename!r} failed size validation")
                raise FileMaxSizeLimitError

            logger.info(
                f"File {file.filename!r}, category: {category!r} validation passed"
            )
            return True
        except EmptyFileError:
            raise
        except FileMaxSizeLimitError:
            raise
        except Exception as e:
            logger.exception(f"Failed to validate file {file.filename!r}: {e}")
            raise ValidateFileFailedError(
                detail=f"Failed to validate file {file.filename}: {str(e)}"
            ) from e


class VirusScanner:
    def __init__(self):
        try:
            self.cd = pyclamd.ClamdNetworkSocket()
            # Проверка соединения (пинг)
            self.cd.ping()
        except Exception as e:
            logger.error(f"Не удалось подключиться к ClamAV: {e}")
            self.cd = None

    async def scan_for_viruses(self, file: UploadFile):
        try:
            logger.debug(f"Scanning file {file.filename!r} for viruses")

            if not file or not file.filename:
                raise EmptyFileError("File is empty or has no name")

            if self.cd is None:
                logger.error("Antivirus service unavailable (self.cd is None)")
                raise VirusScanFileFailedError("Virus scan service is not initialized")

            # Читаем содержимое
            content = await file.read()

            # Сканируем буфер
            try:
                result = self.cd.scan_stream(content)
                logger.debug(f"Scan result: {result}")
            except Exception as e:
                logger.exception(f"Failed to send stream to ClamAV: {e}")
                raise VirusScanFileFailedError(f"Scan failed: {str(e)}")

            # Сбрасываем указатель, чтобы файл можно было прочитать снова (например, сохранить на диск)
            await file.seek(0)

            if result:
                status, virus_name = result.get("stream")  # type: ignore
                if status == "FOUND":
                    logger.warning(
                        f"VIRUS DETECTED: {virus_name} in file {file.filename!r}"
                    )
                    raise FileVirusFound(f"Virus {virus_name} found")

            logger.info(f"No viruses detected in file {file.filename!r}")
            return True

        except (EmptyFileError, FileVirusFound, VirusScanFileFailedError):
            raise
        except Exception as e:
            logger.exception(f"Unexpected error during virus scan: {e}")
            raise VirusScanFileFailedError(detail=f"Internal error: {str(e)}")
