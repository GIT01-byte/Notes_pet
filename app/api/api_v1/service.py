from typing import List
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from core.s3_client import s3_client


FILE_MAP = {
    "videos": [".mp4", ".avi", ".webm"],
    "photos": [".jpeg", ".jpg", ".png", ".webp"],
    "audios": [".mp3", ".ogg", ".wav"],
}


class NoteService:
    def get_file_category(self, filename: str):
        extension = Path(filename).suffix
        for category, excentions in FILE_MAP.items():
            if not extension in excentions:
                continue
            return category
        else:
            return "others"

    async def upload_media_files(self, files: List[UploadFile], category: str):
        """Вспомогательная функция для загрузки списка файлов"""
        urls = []
        if not files:
            return urls
        
        for file in files:
            # Проверяем расширение файла
            file_ext = Path(file.filename).suffix # type: ignore
            valid_category = self.get_file_category(file.filename) # type: ignore
            if not category == valid_category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Неподдерживаемый формат файла"
                )
            
            # Генерируем уникальное имя: uuid + оригинальное расширение
            unique_filename = f"{category}/{uuid.uuid4()}{file_ext}"
            
            print(f"Загрузка {category}: {file.filename} -> {unique_filename}")
            
            # Загружаем
            await s3_client.upload_file(
                file=file.file, 
                filename=unique_filename
            )
            
            # Получаем ссылку
            file_url = await s3_client.get_file_url(filename=unique_filename)
            if file_url:
                urls.append(file_url)
                
        return urls
