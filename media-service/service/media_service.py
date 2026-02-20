from uuid import uuid4
import magic
import pyclamd
from fastapi import UploadFile

from core.schemas.files import FileValidation
from utils.constants import (
    AVATARS,
    NOTES_ATTACHMENT_NAME,
    USERS_AVATAR_NAME,
    VIDEOS,
    IMAGES,
    AUDIO,
)
from exceptions.exceptions import (
    EmptyFileError,
    FileCategoryNotSupportedError,
    FileInvalidExtensionError,
    FileMaxSizeLimitError,
    FileVirusFound,
    ProcessFileFailedError,
    ValidateFileFailedError,
    VirusScanFileFailedError,
)

from utils.logging import logger


class FileProcessingService:
    def __init__(self):
        self.metadata_handler = FileMetadataHandler()
        self.validator = FileContentValidator()
        self.generator_filename = GenerateUnigueFilename()
        self.virus_scanner = VirusScanner()

    async def process_file(self, file: UploadFile, upload_context: str):
        try:
            logger.info(f"Обработка файла {file.filename!r}")

            if not file or not file.filename:
                logger.warning("Попытка загрузки пустого файла")
                raise EmptyFileError

            # Проверка на наличие вирусов
            if not await self.virus_scanner.scan_for_viruses(file):
                raise VirusScanFileFailedError

            # Получение категории файла
            category = await self.metadata_handler.get_file_category(
                file=file, upload_context=upload_context,
            )
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
            FileInvalidExtensionError,
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
    async def get_file_category(self, file: UploadFile, upload_context: str) -> str:
        try:
            logger.debug(
                f"Processing file category {file.filename!r}, content-type: {file.content_type}"
            )

            if not file or not file.content_type:
                logger.warning("Attempt to upload empty file")
                raise EmptyFileError

            if file.content_type in VIDEOS["content_types"] and upload_context == NOTES_ATTACHMENT_NAME:
                logger.debug(
                    f"File {file.filename!r} identified as {VIDEOS["category_name"]}"
                )
                return VIDEOS["category_name"]
            elif file.content_type in IMAGES["content_types"] and upload_context == NOTES_ATTACHMENT_NAME:
                logger.debug(
                    f"File {file.filename!r} identified as {IMAGES["category_name"]}"
                )
                return IMAGES["category_name"]
            elif file.content_type in AUDIO["content_types"] and upload_context == NOTES_ATTACHMENT_NAME:
                logger.debug(
                    f"File {file.filename!r} identified as {AUDIO["category_name"]}"
                )
                return AUDIO["category_name"]
            elif file.content_type in AVATARS["content_types"] and upload_context == USERS_AVATAR_NAME:
                logger.debug(
                    f"File {file.filename!r} identified as {AVATARS["category_name"]}"
                )
                return AVATARS["category_name"]
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


# TODO допработать
class FileContentValidator:
    async def _validate_file_integrity(self, file: UploadFile, category: str):
        try:
            logger.debug(
                f"Validating file integrity {file.filename!r}, category: {category}"
            )

            if not file.filename or not category:
                logger.warning(
                    "Attempt to validation file integrity with empty parameters"
                )
                raise EmptyFileError(detail="Empty file or category")

            # Читаем только начало файла для определения типа
            header = await file.read(2048)
            await file.seek(0)  # Сбрасываем указатель сразу!

            # Определяем расширение и MIME через magic
            extension = file.filename.split(".")[-1].lower()
            detected_mime = magic.from_buffer(header, mime=True)
            if not detected_mime:
                logger.warning(f"Failed to detect MIME type for {file.filename!r}")
                raise ValidateFileFailedError(detail="Failed to detect MIME type")

            logger.debug(f"Detected MIME: {detected_mime}, Extension: {extension}")

            # Проверяем, разрешен ли этот тип и соответствие расширению
            if (
                category == "video"
                and detected_mime not in VIDEOS["content_types"]
                and extension not in VIDEOS["extensions"]
            ):
                logger.debug(
                    f"Расширение {extension} - Тип {detected_mime} не соответствует категории {category}"
                )
                raise FileInvalidExtensionError
            elif (
                category == "image"
                and detected_mime not in IMAGES["content_types"]
                and extension not in IMAGES["extensions"]
            ):
                logger.debug(
                    f"Расширение {extension} - Тип {detected_mime} не соответствует категории {category}"
                )
                raise FileInvalidExtensionError
            elif (
                category == "audio"
                and detected_mime not in AUDIO["content_types"]
                and extension not in AUDIO["extensions"]
            ):
                logger.debug(
                    f"Расширение {extension} - Тип {detected_mime} не соответствует категории {category}"
                )
                raise FileInvalidExtensionError
            elif category == "avatar" and (
                detected_mime not in AVATARS["content_types"]
                and extension not in AVATARS["extensions"]
            ):
                logger.debug(
                    f"Расширение {extension} - Тип {detected_mime} не соответствует категории {category}"
                )
                raise FileInvalidExtensionError

            return True
        except (EmptyFileError, ValidateFileFailedError, FileInvalidExtensionError):
            raise
        except Exception as e:
            logger.exception(
                f"Failed to validate file integrity {file.filename!r}: {e}"
            )
            raise ValidateFileFailedError(
                detail=f"Failed to validate file integrity for {file.filename}: {str(e)}"
            ) from e

    async def _validate_file_size(self, file: UploadFile, category: str):
        try:
            logger.debug(
                f"Validating file size {file.filename!r}, category: {category}, size: {file.size} bytes"
            )

            if not file or not file.size:
                logger.warning("Attempt to validate empty file size")
                raise EmptyFileError(detail="Empty file size")

            if category == VIDEOS["category_name"] and file.size <= VIDEOS["max_size"]:
                logger.debug(f"Video file {file.filename!r} size is valid")
                return True
            elif (
                category == IMAGES["category_name"] and file.size <= IMAGES["max_size"]
            ):
                logger.debug(f"Image file {file.filename!r} size is valid")
                return True
            elif category == AUDIO["category_name"] and file.size <= AUDIO["max_size"]:
                logger.debug(f"Audio file {file.filename!r} size is valid")
                return True
            elif (
                category == AVATARS["category_name"]
                and file.size <= AVATARS["max_size"]
            ):
                logger.debug(f"Avatar file {file.filename!r} size is valid")
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
            if not file or not file.filename or not file.size or not category:
                logger.warning("Attempt to validate empty file")
                raise EmptyFileError(detail="Empty file or category")

            if not await self._validate_file_size(file, category):
                logger.error(f"File {file.filename!r} failed size validation")
                raise FileMaxSizeLimitError

            if not await self._validate_file_integrity(file, category):
                logger.error(f"File {file.filename!r} failed integrity validation")
                raise ValidateFileFailedError

            logger.info(
                f"File {file.filename!r}, category: {category!r} validation passed"
            )
            return True
        except (
            EmptyFileError,
            FileMaxSizeLimitError,
            FileInvalidExtensionError,
        ):
            raise
        except Exception as e:
            logger.exception(f"Failed to validate file {file.filename!r}: {e}")
            raise ValidateFileFailedError(
                detail=f"Failed to validate file {file.filename}: {str(e)}"
            ) from e


class VirusScanner:
    def __init__(self):
        try:
            self.cd = pyclamd.ClamdUnixSocket()
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
