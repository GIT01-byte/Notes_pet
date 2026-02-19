from uuid import UUID, uuid7

from fastapi import (
    Depends,
    APIRouter,
    Response,
)

from core.config import settings
from core.schemas.files import (
    FileMeatadataCreate,
    FileMeatadataRead,
)
from core.s3.s3_client import s3_client

from exceptions.exceptions import (
    EmptyFileError,
    FileInvalidExtensionError,
    FileMaxSizeLimitError,
    FileVirusFound,
    ValidateFileFailedError,
    VirusScanFileFailedError,
    FileCategoryNotSupportedError,
    FileCategoryNotSupportedError,
    FilesUploadFailedError,
    ViewFileFailedError,
)

from utils.constants import NOTES_ATTACHMENT_NAME, USERS_AVATAR_NAME
from service.media_service import FileProcessingService
from service.media_repo import MediaRepo

from .deps import FileUploadRequest

from utils.logging import logger


router = APIRouter(prefix=settings.api.v1.service, tags=["Media Service"])

# ----- Основные API ендпоинты -----
# | Method | Endpoint | Description | Request body |
# | POST | /upload | Загрузка файла | multipart/form-data (file, bucket/folder_name) |
# | GET | /files/{file_uuid} | Получение метаданных о файле | Возвращает JSON: URL, размер, тип, дату загрузки |
# | GET | /files/{file_uuid}/view | Прямая ссылка или редирект на файл | Позволяет просматривать файл в браузере |
# | DELETE | /files/{file_uuid} | Удаление файла | Удаляет файл из S3 и запись из базы данных |

# TODO all: сделать синхронную отправку и в БД и в S3
# TODO all: сделать статус "uploaded" после того как файл был успешно отправлен в S3


@router.get("/health_check/")
async def health_check():
    return {"success": "Медиа-сервис запущен"}


@router.post("/upload")
async def upload_file(request: FileUploadRequest = Depends()):
    media_service = FileProcessingService()
    try:
        logger.info(f"Загрузка файла {request.file.filename!r} в S3")

        if not request.file:
            logger.warning("Попытка загрузки пустого файла")
            raise EmptyFileError

        # Валидация и генерация уникального имени файла
        validation_process_file = await media_service.process_file(
            file=request.file, upload_context=request.upload_context
        )

        unigue_filename = validation_process_file.filename
        category = validation_process_file.category

        if not unigue_filename:
            logger.error(
                f"Ошибка при генерации уникального имени файла {request.file.filename!r}"
            )
            raise FilesUploadFailedError(
                detail=f"Generate unigue filename error for file {request.file.filename!r}"
            )

        # Отправка файла в S3
        upload_key = f"{request.upload_context}/{request.entity_id}/{unigue_filename}"
        if request.upload_context == NOTES_ATTACHMENT_NAME:
            logger.info(f"Файл {request.file.filename!r} будет сохранен как post_attachment")
            await s3_client.upload_file(
                file=request.file.file,
                key=upload_key,
            )
            logger.info(f"Файл {request.file.filename!r} успешно загружен в S3")
        
        elif request.upload_context == USERS_AVATAR_NAME:
            logger.info(f"Файл {request.file.filename!r} будет сохранен как avatar")
            await s3_client.upload_file(
                file=request.file.file,
                key=upload_key,
            )
            logger.info(f"Файл {request.file.filename!r} успешно загружен в S3")
            
        else:
            raise FilesUploadFailedError(f"Unknown upload context: {request.upload_context}")

        # Формирование метаданных файла
        uuid = uuid7()
        s3_url = await s3_client.get_file_url(key=upload_key)
        status = "uploaded" # FIXME

        if not (uuid and s3_url and request.file.size and request.file.content_type):
            logger.error(
                f"Ошибка при формировании метаданных файла {request.file.filename!r}"
            )
            raise FilesUploadFailedError(
                detail="Не удалось сформировать метаданные файла"
            )

        new_file_metadata = FileMeatadataCreate(
            uuid=uuid,
            s3_url=s3_url,
            filename=unigue_filename,
            size=request.file.size,
            content_type=request.file.content_type,
            category=category,
            status=status,
        )
        logger.debug(f"Метаданные файла {request.file.filename!r} успешно сформированы")

        # Запись метаданных в БД
        file_metadata_in_db = await MediaRepo.create_metadata(
            file_metadata_to_create=new_file_metadata
        )

        if not file_metadata_in_db:
            logger.error(
                f"Ошибка при сохранении метаданных файла {request.file.filename!r} в БД"
            )
            raise FilesUploadFailedError(detail="Не удалось сохранить метаданные в БД")

        logger.info(f"Файл {request.file.filename!r} успешно загружен, UUID: {uuid}")
        return {
            "ok": True,
            "message": f"Файл {request.file.filename!r} успешно загружен",
            "file": {
                "uuid": str(file_metadata_in_db.uuid),
                "s3_url": file_metadata_in_db.s3_url,
                "content_type": file_metadata_in_db.content_type,
                "category": file_metadata_in_db.category,
                "uploaded_at": str(file_metadata_in_db.created_at_db),
            }
        }

    except (
        EmptyFileError,
        FileCategoryNotSupportedError,
        FileMaxSizeLimitError,
        FileVirusFound,
        FileInvalidExtensionError,
        ValidateFileFailedError,
        VirusScanFileFailedError,
        FilesUploadFailedError,
    ):
        raise
    except Exception as e:
        logger.exception(
            f"Неожиданная ошибка при загрузке файла {request.file.filename!r}: {e}"
        )
        raise FilesUploadFailedError from e


@router.get("/files/{file_uuid}/", response_model=FileMeatadataRead)
async def get_file(file_uuid: UUID):
    try:
        logger.info(f"Получение метаданных файла с UUID: {file_uuid}")

        file_db = await MediaRepo.get_files_metadata(file_uuid=file_uuid)

        if not file_db:
            logger.warning(f"Файл с UUID: {file_uuid} не найден")
            raise ViewFileFailedError(detail=f"Файл с UUID {file_uuid} не найден")

        logger.info(f"Метаданные файла {file_uuid} успешно получены")
        return file_db

    except ViewFileFailedError:
        raise
    except Exception as e:
        logger.exception(
            f"Неожиданная ошибка при получении метаданных файла {file_uuid}: {e}"
        )
        raise ViewFileFailedError from e


@router.get("/files/{file_uuid}/view/")
async def view_file_urL(file_uuid: UUID):
    try:
        logger.info(f"Получение прямой ссылки на файл с UUID: {file_uuid}")

        file_db = await MediaRepo.get_files_metadata(file_uuid=file_uuid)

        if not file_db:
            logger.warning(f"Файл с UUID: {file_uuid} не найден")
            raise ViewFileFailedError(detail=f"Файл с UUID {file_uuid} не найден")

        file_url = file_db.s3_url
        if not file_url:
            logger.error(f"Отсутствует S3 URL для файла {file_uuid}")
            raise ViewFileFailedError(detail="S3 URL не найден")

        logger.info(f"Ссылка на файл {file_uuid} успешно получена")
        return Response(status_code=302, headers={"Location": file_url})

    except ViewFileFailedError:
        raise
    except Exception as e:
        logger.exception(
            f"Неожиданная ошибка при получении ссылки на файл {file_uuid}: {e}"
        )
        raise ViewFileFailedError from e


@router.delete("/files/delete/{file_uuid}/")
async def delete_file(file_uuid: UUID):
    try:
        logger.info(f"Удаление файла с UUID: {file_uuid}")

        file_db = await MediaRepo.get_files_metadata(file_uuid=file_uuid)

        if not file_db:
            logger.warning(f"Файл с UUID: {file_uuid} не найден")
            raise ViewFileFailedError(detail=f"Файл с UUID {file_uuid} не найден")

        # Удаление файла из S3
        await s3_client.delete_file(key=file_db.filename)
        logger.info(f"Файл {file_db.filename!r} успешно удален из S3")

        # Удаление записи из БД
        await MediaRepo.delete_file_metadata(file_metadata_obj=file_db)
        logger.info(f"Метаданные файла {file_uuid} успешно удалены из БД")

        return {"ok": True, "message": f"Файл {file_db.filename!r} успешно удален"}

    except ViewFileFailedError:
        raise
    except Exception as e:
        logger.exception(f"Неожиданная ошибка при удалении файла {file_uuid}: {e}")
        raise ViewFileFailedError from e
