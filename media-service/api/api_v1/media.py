from fastapi import Depends, APIRouter

from core.config import settings

from core.schemas.files import (
    FileCreate,
)

from service.service import MediaService
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


@router.post("/upload")
async def upload_file(reauest: FileUploadRequest = Depends()):
    media_sevice = MediaService()
    
    await media_sevice.upload_file(
        file=reauest.file,
        filename=reauest.filename,
    )
    
    return {"message": f"File {reauest.file} uploaded successfully"}
