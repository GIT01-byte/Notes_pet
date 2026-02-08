from uuid import UUID
from fastapi import UploadFile

from core.s3.s3_client import s3_client

from .media_repo import MediaRepo

# Сделать проверку целостности и обработку файлов
class MediaService:
    pass