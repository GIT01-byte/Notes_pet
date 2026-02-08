from uuid import UUID, uuid7

from fastapi import Depends, APIRouter

from core.config import settings

from core.schemas.files import (
    FileMeatadataCreate,
)

from service.media_service import MediaService
from service.media_repo import MediaRepo
from .deps import FileUploadRequest

from utils.logging import logger

router = APIRouter(prefix=settings.api.v1.handler, tags=["File Handler"])

# | POST | /upload | Загрузка файла | multipart/form-data (file, bucket/folder_name) |
# | GET | /files/{id} | Получение метаданных о файле | Возвращает JSON: URL, размер, тип, дату загрузки |
# | GET | /files/{id}/view | Прямая ссылка или редирект на файл | Позволяет просматривать файл в браузере |
# | DELETE | /files/{id} | Удаление файла | Удаляет файл из S3 и запись из базы данных |

@router.get("/health_check")
async def health_check():
    return {"success": "Медиа-сервис запущен"}

# TODO: Сделать нормальную обработку ошибок и логирование + доделать запись в БД
@router.post("/upload")
async def upload_file(request: FileUploadRequest = Depends()):
    media_sevice = MediaService()

    try:
        logger.info(f"Загрузка файла {request.file} в бакет {request.filename}")
        
        # Отправка файла в S3
        await media_sevice.upload_file(
            file=request.file,
            filename=request.filename,
        )
        logger.info(f"Файл {request.file} успешно загружен")
        
        # Формирование метаданных файла с жесткой проверкой на целостность
        uuid = uuid7()
        s3_url = await media_sevice.get_s3_url(filename=request.filename)
        
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
            file_metadata_in_db = await MediaRepo.create_note(file_metadata_to_create=new_file_metadata)
            
            if file_metadata_in_db:
                logger.info(f"Метаданные файла: {request.file} сохранены в БД")
                return {
                    "ok": True,
                    "message": f"Файл {request.file} успешно загружен"
                }
            logger.error(f"Ошибка при сохранении метаданных файла: {request.file} в БД")
            raise Exception("Ошибка при сохранении метаданных в БД")
        logger.error(f"Ошибка при получении метаданных файла: {request.file}")
        raise Exception("Ошибка при получении метаданных")
        
    except:
        return {
            "ok": False,
            "message": f"Ошибка при загрузке файла {request.file}"
        }
        
        
@router.post("/files/{id}")
async def view_file(file_id: UUID):
    media_sevice = MediaService()

    try:
        logger.info(f"Просмотр файла {file_id}")
        
        view_file = await media_sevice.view_file(file_id=file_id)
    except:
        return {
            "ok": False,
            "message": f"Ошибка при просмотре файла {file_id}"
        }
