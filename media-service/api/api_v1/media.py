from uuid import uuid7

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
    return {"success": "Media service is started"}

# TODO: Сделать нормальную обработку ошибок и логирование + доделать запись в БД
@router.post("/upload")
async def upload_file(request: FileUploadRequest = Depends()):
    media_sevice = MediaService()

    try:
        logger.info(f"Uploading file {request.file} to bucket {request.filename}")
        
        # Отправка файла в S3
        await media_sevice.upload_file(
            file=request.file,
            filename=request.filename,
        )
        logger.info(f"File {request.file} uploaded successfully")
        
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
            logger.info(f"Metadata of file: {request.file} is succesfully forming")
        else:
            logger.error(f"Error while getting metadata of file: {request.file}")
        
        # Запись метаданных в БД
        
        logger.info(f"Metadata of file: {request.file} is saved in DB")
        return {
            "ok": True,
            "message": f"File {request.file} uploaded successfully"
        }
    except:
        return {
            "ok": False,
            "message": f"Error while uploading file {request.file}"
        }
        
        
@router.post("/files/{id}")
async def view_file(reauest: FileUploadRequest = Depends()):
    media_sevice = MediaService()

    try:
        logger.info(f"Uploading file {reauest.file} to bucket {reauest.filename}")
        
        await media_sevice.upload_file(
            file=reauest.file,
            filename=reauest.filename,
        )
        logger.info(f"File {reauest.file} uploaded successfully")
        
        return {
            "ok": True,
            "message": f"File {reauest.file} uploaded successfully"
        }
    except:
        return {
            "ok": False,
            "message": f"Error while uploading file {reauest.file}"
        }