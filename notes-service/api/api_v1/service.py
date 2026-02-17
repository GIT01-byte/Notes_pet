from typing import List
import uuid

from fastapi import HTTPException, UploadFile

from exceptions.exceptions import (
    FilesUploadError,
    FilesHandlingError,
)
from core.models_crud.models_cruds import media_uuid

from integrations.files.files import get_file, upload_file
from integrations.files.schemas import NotesServiceFileUploadRequest

from utils.logging import logger


class NoteService:
    async def upload_media_files(
        self, files: List[UploadFile], category: str, note_uuid: str
    ) -> list:
        """Вспомогательная функция для загрузки списка файлов"""
        if not files:
            logger.warning("Список файлов пуст")
            return []

        logger.info(f"Начало загрузки {len(files)} файлов категории {category}")

        try:
            file_uuids = []
            for file in files:
                request = NotesServiceFileUploadRequest(
                    upload_context="post_attachment", file=file, entity_uuid=note_uuid
                )
                logger.debug(f"Запрос для загрузки {category}: {request}")

                response = await upload_file(request)
                file_uuids.append(response["uuid"])

            return file_uuids
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка загрузки файлов категории {category}: {e}")
            raise FilesUploadError

    async def get_files_metadata(self, files_uuids: List[str]) -> List[dict]:
        """Вспомогательная функция для получения метаданных файлов по их UUID"""
        if not files_uuids:
            logger.warning("Список UUID файлов пуст")
            return []

        try:
            logger.info(f"Получение метаданных для {len(files_uuids)} файлов")
            metadata_list = []
            for file_uuid in files_uuids:
                file_data = await get_file(file_uuid)
                metadata_list.append(file_data)
            return metadata_list
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка получения метаданных файлов: {e}")
            raise FilesHandlingError
