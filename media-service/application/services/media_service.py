# from fastapi import UploadFile
# from sqlalchemy.ext.asyncio import AsyncSession

# from application.configs.settings import settings
# from application.core.schemas.files import FileMeatadataCreate
# from application.exceptions.base import BaseAPIException
# from application.exceptions.exceptions import (
#     FilesUploadFailedError,
# )
# from application.rabbitmq.contracts.files import (
#     FileCreatedMessage,
#     FilesOutboxCreateBody,
#     FilesOutboxMessageName,
# )
# from application.repositories.database.models.files import FilesMetadataOrm
# from application.repositories.database.models.files_outbox import (
#     FilesOutboxOrm,
#     FilesOutboxStatusesEnum,
# )
# from application.repositories.files_outbox_repository import FilesOutboxRepository
# from application.repositories.files_repository import FileRepository
# from application.s3.s3_client import S3Client
# from application.utils.constants import (
#     NOTES_ATTACHMENT_NAME,
#     USERS_AVATAR_NAME,
# )
# from application.utils.logging import logger


# # TODO переделать архиеткруты, добавить use cases
# class FileUploadService:
#     def __init__(
#         self,
#         session: AsyncSession,
#         s3_client: S3Client,
#     ):
#         file_meta_repo = FileRepository(session=session)
#         file_outbox_repo = FilesOutboxRepository(session=session)
#         self.file_meta_repo = file_meta_repo
#         self.file_outbox_repo = file_outbox_repo
#         self.session = session
#         self.s3_client = s3_client

#     async def process_create_DB_record(
#         self,
#         file_metadata: FileMeatadataCreate,
#         s3_temp_upload_key: str,
#         s3_upload_key: str,
#         upload_context: str,
#     ) -> tuple[FilesMetadataOrm, FilesOutboxOrm]:
#         try:
#             logger.info(f"Создание записи в БД для файла: {file_metadata.file_id}")

#             file_metadata_in_db = await self.file_meta_repo.create_metadata(
#                 file_metadata_to_create=file_metadata
#             )
#             if not file_metadata_in_db:
#                 raise FilesUploadFailedError(
#                     detail="Не удалось сохранить метаданные в БД"
#                 )

#             message_body = FilesOutboxCreateBody(
#                 file_id=str(file_metadata.file_id),
#                 upload_context=upload_context,
#                 s3_temp_upload_key=s3_temp_upload_key,
#                 s3_upload_key=s3_upload_key,
#                 status=FilesOutboxStatusesEnum.PENDING.value,
#             )
#             message = FileCreatedMessage(
#                 sender=settings.service.name,  # TODO доработать
#                 body=message_body,
#             )

#             file_message_outbox = await self.file_outbox_repo.create_outbox_message(
#                 message_name=FilesOutboxMessageName.upload_start.value,
#                 body=message.model_dump(mode="json"),
#             )
#             if not file_message_outbox:
#                 raise FilesUploadFailedError(
#                     detail="Не удалось сохранить сообщение для отправки файла в Outbox"
#                 )

#             await self.session.commit()
#             logger.info(f"Запись в БД успешно создана: {file_metadata.file_id}")
#             return (file_metadata_in_db, file_message_outbox)
#         except BaseAPIException:
#             await self.session.rollback()
#             raise
#         except Exception as e:
#             logger.exception(f"Ошибка при создании метаданных файла: {e}")
#             await self.session.rollback()
#             raise FilesUploadFailedError(
#                 detail=f"Произошла ошибка при создании метаданных файла: {e}"
#             )

#     async def temp_upload_s3(self, file: UploadFile, s3_temp_upload_key: str):
#         try:
#             logger.info(
#                 f"Загрузка файла во временное хранилище S3: {s3_temp_upload_key}"
#             )

#             await self.s3_client.upload_file(
#                 file=file.file,
#                 key=s3_temp_upload_key,
#             )
#             logger.info(f"Файл загружен во временное хранилище: {s3_temp_upload_key}")
#         except Exception as e:
#             logger.exception(f"Ошибка загрузки файла во временную папку S3: {e}")
#             raise FilesUploadFailedError(
#                 detail=f"Failed to upload file {s3_temp_upload_key} to temporary S3 folder"
#             )

#     async def upload_s3(
#         self,
#         file: UploadFile,
#         file_id: str,
#         upload_context: str,
#         upload_key: str,
#     ):
#         try:
#             if upload_context == NOTES_ATTACHMENT_NAME:
#                 await self.s3_client.upload_file(
#                     file=file.file,
#                     key=upload_key,
#                 )
#             elif upload_context == USERS_AVATAR_NAME:
#                 await self.s3_client.upload_file(
#                     file=file.file,
#                     key=upload_key,
#                 )
#             else:
#                 raise FilesUploadFailedError(
#                     f"Unknown upload context: {upload_context}"
#                 )
#         except Exception as e:
#             logger.exception(f"Ошибка загрузки файла в постоянное хранилище S3: {e}")
#             raise FilesUploadFailedError(
#                 detail=f"Failed to upload file {file_id} to permanent S3 storage"
#             )

#     async def get_file_url(self, s3_upload_key: str) -> str:
#         try:
#             file_url = await self.s3_client.get_file_url(key=s3_upload_key)
#             return file_url
#         except Exception as e:
#             logger.exception(f"Ошибка получения URL файла: {e}")
#             raise FilesUploadFailedError(
#                 detail=f"Failed to get file URL for {s3_upload_key}"
#             )

#     # async def finalize_upload_file(
#     #     self,
#     #     unigue_filename: str,
#     #     upload_context: str,
#     #     entity_id: int,
#     # ):
#     #     # Принятие результата обработки RabbitMQ сообщения
#     #     # Перенос файла из временной папки в постоянную
#     #     # Обновление записей в БД
#     #     s3_upload_key = f"{upload_context}/{entity_id}/{unigue_filename}"
#     #     s3_url = await s3_client.get_file_url(key=s3_upload_key)


# # class FileProcessingService:
# #     def __init__(self):
# #         self.metadata_handler = FileMetadataHandler()
# #         self.validator = FileContentValidator()
# #         self.generator_filename = FileGenerateFilename()
# #         self.virus_scanner = VirusScanner()

# #     async def process_file(self, file: UploadFile, upload_context: str):
# #         try:
# #             logger.info(f"Начало обработки файла: {file.filename}")

# #             if not file or not file.filename:
# #                 raise EmptyFileError

# #             if not await self.virus_scanner.scan_for_viruses(file):
# #                 raise VirusScanFileFailedError

# #             category = await self.metadata_handler.get_file_category(
# #                 file=file,
# #                 upload_context=upload_context,
# #             )
# #             if not category:
# #                 raise ValidateFileFailedError(
# #                     detail=f"Catagory handling error for file {file.filename!r}"
# #                 )

# #             if not await self.validator.validate_file(file, category):
# #                 raise ValidateFileFailedError

# #             file_id = str(uuid7())

# #             s3_temp_upload_key = (
# #                 await self.generator_filename.generate_s3_temp_upload_key(
# #                     file=file, file_id=file_id
# #                 )
# #             )

# #             unigue_filename = await self.generator_filename.generate_unigue_filename(
# #                 file=file, category=category, file_id=file_id
# #             )
# #             if not unigue_filename:
# #                 raise ValidateFileFailedError(
# #                     detail=f"Uniqque filename generation error for file {file.filename!r}"
# #                 )

# #             logger.info(f"Файл успешно обработан: {file.filename}, ID: {file_id}")
# #             return FileValidation(
# #                 validaion_status=True,
# #                 category=category,
# #                 unique_filename=unigue_filename,
# #                 s3_temp_upload_key=s3_temp_upload_key,
# #                 file_id=file_id,
# #             )
# #         except BaseAPIException:
# #             raise
# #         except Exception as e:
# #             logger.exception(f"Ошибка обработки файла: {e}")
# #             raise ProcessFileFailedError(
# #                 detail=f"Failed to process file {file.filename}: {str(e)}"
# #             ) from e


# # class FileMetadataHandler:
# #     async def get_file_category(self, file: UploadFile, upload_context: str) -> str:
# #         try:
# #             if not file or not file.content_type:
# #                 raise EmptyFileError

# #             if (
# #                 file.content_type in VIDEOS["content_types"]
# #                 and upload_context == NOTES_ATTACHMENT_NAME
# #             ):
# #                 return VIDEOS["category_name"]
# #             elif (
# #                 file.content_type in IMAGES["content_types"]
# #                 and upload_context == NOTES_ATTACHMENT_NAME
# #             ):
# #                 return IMAGES["category_name"]
# #             elif (
# #                 file.content_type in AUDIO["content_types"]
# #                 and upload_context == NOTES_ATTACHMENT_NAME
# #             ):
# #                 return AUDIO["category_name"]
# #             elif (
# #                 file.content_type in AVATARS["content_types"]
# #                 and upload_context == USERS_AVATAR_NAME
# #             ):
# #                 return AVATARS["category_name"]
# #             else:
# #                 raise FileCategoryNotSupportedError
# #         except BaseAPIException:
# #             raise
# #         except Exception as e:
# #             logger.exception(f"Ошибка определения категории файла: {e}")
# #             raise ValidateFileFailedError(
# #                 detail=f"Failed to process file category for {file.filename}: {str(e)}"
# #             ) from e


# # class FileGenerateFilename:
# #     # TODO сделать так, чтобы file_id был одинаков как и БД так и в названии файла
# #     async def generate_unigue_filename(
# #         self, file: UploadFile, file_id: str, category: str
# #     ) -> str:
# #         try:
# #             if not file.filename or not category:
# #                 raise EmptyFileError(detail="Empty filename or category")

# #             extension = file.filename.split(".")[-1].lower()

# #             if not extension:
# #                 raise EmptyFileError(detail=f"File {file.filename!r} has no extension")

# #             new_filename = f"{category}/{file_id}.{extension}"
# #             return new_filename
# #         except BaseAPIException:
# #             raise
# #         except Exception as e:
# #             logger.exception(f"Ошибка генерации уникального имени файла: {e}")
# #             raise ValidateFileFailedError(
# #                 detail=f"Failed to generate unique filename for {file.filename}: {str(e)}"
# #             ) from e

# #     async def generate_s3_temp_upload_key(self, file: UploadFile, file_id: str) -> str:
# #         try:
# #             if not file.filename:
# #                 raise EmptyFileError(detail="Empty filename")

# #             extension = file.filename.split(".")[-1].lower()

# #             if not extension:
# #                 raise EmptyFileError(detail=f"File {file.filename!r} has no extension")

# #             s3_temp_upload_key = f"temp/{file_id}.{extension}"
# #             return s3_temp_upload_key
# #         except BaseAPIException:
# #             raise
# #         except Exception as e:
# #             logger.exception(f"Ошибка генерации временного ключа S3: {e}")
# #             raise ValidateFileFailedError(
# #                 detail=f"Failed to generate temp s3 upload key for {file.filename}: {str(e)}"
# #             ) from e


# # TODO допработать
# # class FileContentValidator:
# #     async def _validate_file_integrity(self, file: UploadFile, category: str):
# #         try:
# #             if not file.filename or not category:
# #                 raise EmptyFileError(detail="Empty file or category")

# #             header = await file.read(2048)
# #             await file.seek(0)

# #             extension = file.filename.split(".")[-1].lower()
# #             detected_mime = magic.from_buffer(header, mime=True)
# #             if not detected_mime:
# #                 raise ValidateFileFailedError(detail="Failed to detect MIME type")

# #             if (
# #                 category == "video"
# #                 and detected_mime not in VIDEOS["content_types"]
# #                 and extension not in VIDEOS["extensions"]
# #             ):
# #                 raise FileInvalidExtensionError
# #             elif (
# #                 category == "image"
# #                 and detected_mime not in IMAGES["content_types"]
# #                 and extension not in IMAGES["extensions"]
# #             ):
# #                 raise FileInvalidExtensionError
# #             elif (
# #                 category == "audio"
# #                 and detected_mime not in AUDIO["content_types"]
# #                 and extension not in AUDIO["extensions"]
# #             ):
# #                 raise FileInvalidExtensionError
# #             elif category == "avatar" and (
# #                 detected_mime not in AVATARS["content_types"]
# #                 and extension not in AVATARS["extensions"]
# #             ):
# #                 raise FileInvalidExtensionError

# #             return True
# #         except BaseAPIException:
# #             raise
# #         except Exception as e:
# #             logger.exception(f"Ошибка проверки целостности файла: {e}")
# #             raise ValidateFileFailedError(
# #                 detail=f"Failed to validate file integrity for {file.filename}: {str(e)}"
# #             ) from e

# #     async def _validate_file_size(self, file: UploadFile, category: str):
# #         try:
# #             if not file or not file.size:
# #                 raise EmptyFileError(detail="Empty file size")

# #             if category == VIDEOS["category_name"] and file.size <= VIDEOS["max_size"]:
# #                 return True
# #             elif (
# #                 category == IMAGES["category_name"] and file.size <= IMAGES["max_size"]
# #             ):
# #                 return True
# #             elif category == AUDIO["category_name"] and file.size <= AUDIO["max_size"]:
# #                 return True
# #             elif (
# #                 category == AVATARS["category_name"]
# #                 and file.size <= AVATARS["max_size"]
# #             ):
# #                 return True
# #             else:
# #                 return False
# #         except BaseAPIException:
# #             raise
# #         except Exception as e:
# #             logger.exception(f"Ошибка проверки размера файла: {e}")
# #             raise ValidateFileFailedError(
# #                 detail=f"Failed to validate file size for {file.filename}: {str(e)}"
# #             ) from e

# #     async def validate_file(self, file: UploadFile, category: str):
# #         try:
# #             if not file or not file.filename or not file.size or not category:
# #                 raise EmptyFileError(detail="Empty file or category")

# #             if not await self._validate_file_size(file, category):
# #                 raise FileMaxSizeLimitError

# #             if not await self._validate_file_integrity(file, category):
# #                 raise ValidateFileFailedError

# #             return True
# #         except BaseAPIException:
# #             raise
# #         except Exception as e:
# #             logger.exception(f"Ошибка валидации файла: {e}")
# #             raise ValidateFileFailedError(
# #                 detail=f"Failed to validate file {file.filename}: {str(e)}"
# #             ) from e


# # class VirusScanner:
# #     def __init__(self):
# #         try:
# #             self.cd = pyclamd.ClamdUnixSocket()
# #             self.cd.ping()
# #         except Exception as e:
# #             logger.error(f"Не удалось подключиться к ClamAV: {e}")
# #             self.cd = None

# #     async def scan_for_viruses(self, file: UploadFile):
# #         try:
# #             if not file or not file.filename:
# #                 raise EmptyFileError("File is empty or has no name")

# #             if self.cd is None:
# #                 logger.error("Antivirus service unavailable")
# #                 raise VirusScanFileFailedError("Virus scan service is not initialized")

# #             content = await file.read()

# #             try:
# #                 result = self.cd.scan_stream(content)
# #             except Exception as e:
# #                 logger.exception(f"Ошибка отправки файла в ClamAV: {e}")
# #                 raise VirusScanFileFailedError(f"Scan failed: {str(e)}")

# #             await file.seek(0)

# #             if result:
# #                 status, virus_name = result.get("stream")  # type: ignore
# #                 if status == "FOUND":
# #                     logger.warning(f"ВИРУС ОБНАРУЖЕН: {virus_name}")
# #                     raise FileVirusFound(f"Virus {virus_name} found")

# #             return True

# #         except BaseAPIException:
# #             raise
# #         except Exception as e:
# #             logger.exception(f"Ошибка сканирования на вирусы: {e}")
# #             raise VirusScanFileFailedError(detail=f"Internal error: {str(e)}")
