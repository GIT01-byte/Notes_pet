from uuid import UUID, uuid7

from fastapi import Depends, APIRouter, Response

from core.config import settings
from core.schemas.files import (
    FileMeatadataCreate,
    FileMeatadataRead,
)
from core.s3.s3_client import s3_client

from exceptions.exceptions import (
    FilesUploadFailedError,
    ViewFileFailedError,
)

from service.media_service import MediaService
from service.media_repo import MediaRepo

from .deps import FileUploadRequest

from utils.logging import logger


router = APIRouter(prefix=settings.api.v1.service, tags=["Media Service"])

# | POST | /upload | Загрузка файла | multipart/form-data (file, bucket/folder_name) |
# | GET | /files/{file_uuid} | Получение метаданных о файле | Возвращает JSON: URL, размер, тип, дату загрузки |
# | GET | /files/{file_uuid}/view | Прямая ссылка или редирект на файл | Позволяет просматривать файл в браузере |
# | DELETE | /files/{file_uuid} | Удаление файла | Удаляет файл из S3 и запись из базы данных |
# TODO сделать синхронную отправку и в БД и в S3


@router.get("/health_check")
async def health_check():
    return {"success": "Медиа-сервис запущен"}


# TODO: Сделать нормальную обработку ошибок и логирование
@router.post("/upload")
async def upload_file(request: FileUploadRequest = Depends()):
    try:
        logger.info(f"Загрузка файла {request.file} в бакет {request.filename}")

        # Отправка файла в S3
        await s3_client.upload_file(
            file=request.file.file,
            filename=request.filename,
        )
        logger.info(f"Файл {request.file} успешно загружен")

        # Формирование метаданных файла с жесткой проверкой на целостность
        uuid = uuid7()
        s3_url = await s3_client.get_file_url(filename=request.filename)

        if uuid and s3_url and request.file.size and request.file.content_type:
            new_file_metadata = FileMeatadataCreate(
                uuid=uuid,
                s3_url=s3_url,
                filename=request.filename,
                size=request.file.size,
                content_type=request.file.content_type,
            )
            logger.info(f"Метаданные файла: {request.file} успешно сформированы")

            # Запись метаданных в БД
            file_metadata_in_db = await MediaRepo.create_note(
                file_metadata_to_create=new_file_metadata
            )

            if file_metadata_in_db:
                logger.info(f"Метаданные файла: {request.file} сохранены в БД")
                return {"ok": True, "message": f"Файл {request.file.filename!r} успешно загружен"}
            # Exception Handling
        # Exception Handling

    except:
        # Exception Handling
        return FilesUploadFailedError


@router.get("/files/{file_uuid}", response_model=FileMeatadataRead)
async def get_file(file_uuid: UUID):
    try:
        logger.info(f"Просмотр файла {file_uuid}")

        file_db = await MediaRepo.get_files_metadata(file_uuid=file_uuid)
        if file_db:
            logger.info(f"Файл {file_uuid} успешно найден")
            return file_db
        # Exception Handling
    except:
        # Exception Handling
        return ViewFileFailedError

@router.get("/files/{file_uuid}/view")
async def view_file_urL(file_uuid: UUID):
    try:
        logger.info(f"Получение прямой ссылки на файл {file_uuid}")
        
        file_db = await MediaRepo.get_files_metadata(file_uuid=file_uuid)
        if file_db:
            logger.info(f"Файл {file_uuid} успешно найден")
            file_url = file_db.s3_url
            if file_url:
                logger.info(f"Ссылка на файл {file_uuid} успешно получена")
                redirect_response = Response(status_code=302, headers={"Location": file_url})
                return redirect_response
        # Exception Handling
    except:
        # Exception Handling
        return ViewFileFailedError(detail="Error viewing file url")
        
        