from typing import List
from uuid import UUID

from fastapi import HTTPException, UploadFile

from exceptions.exceptions import (
    EmptyFileError,
    FilesHandlingError,
    FilesUploadError,
    RepositoryInternalError,
)

from integrations.files.files import get_file, upload_file
from integrations.files.schemas import (
    NotesServiceFileUploadRequest,
    NotesServiceFileUploadResponse,
)
from integrations.files.constants import (
    VIDEO_FILES_NAME,
    IMAGE_FILES_NAME,
    AUDIO_FILES_NAME,
)

from core.media_files_repo import MediaFilesRepo

from utils.logging import logger


class NoteService:
    async def _upload_media_file(
        self, file: UploadFile, entity_id: int
    ) -> NotesServiceFileUploadResponse:
        """Загрузка файла в S3 через Media service"""
        try:
            request = NotesServiceFileUploadRequest(
                upload_context="post_attachment", file=file, entity_id=entity_id
            )
            response = await upload_file(request)
            if not response:
                raise FilesUploadError(f"No response for {file.filename}")
            logger.info(f"Файл {file.filename} загружен в S3")
            return response
        except (HTTPException, FilesUploadError):
            raise
        except Exception as e:
            logger.exception(f"Ошибка загрузки {file.filename}: {e}")
            raise FilesUploadError from e

    async def _save_file_to_db(
        self, note_id: int, file_data: NotesServiceFileUploadResponse, category: str
    ) -> UUID:
        """Сохранение метаданных файла в БД"""
        try:
            match category:
                case category if category == VIDEO_FILES_NAME:
                    result = await MediaFilesRepo.add_video(note_id=note_id, file_data=file_data)
                case category if category == IMAGE_FILES_NAME:
                    result = await MediaFilesRepo.add_image(note_id=note_id, file_data=file_data)
                case category if category == AUDIO_FILES_NAME:
                    result = await MediaFilesRepo.add_audio(note_id=note_id, file_data=file_data)
                case _:
                    raise FilesHandlingError(f"Unknown category: {category}")

            if not result:
                raise RepositoryInternalError(f"Failed to save {category} file")
            
            logger.info(f"Файл {file_data.uuid} сохранен в БД")
            return result.uuid
        except (FilesHandlingError, RepositoryInternalError):
            raise
        except Exception as e:
            logger.exception(f"Ошибка сохранения {file_data.uuid}: {e}")
            raise RepositoryInternalError from e

    async def process_media_files(
        self, files: List[UploadFile], category: str, note_id: int
    ) -> list[UUID]:
        """Обработка и сохранение медиафайлов"""
        try:
            if not files:
                raise EmptyFileError

            logger.info(f"Обработка {len(files)} файлов категории {category} для заметки {note_id}")
            
            uploaded_uuids = []
            for file in files:
                # Загружаем в S3
                upload_response = await self._upload_media_file(file=file, entity_id=note_id)
                if not upload_response:
                    raise FilesUploadError(f"No upload response for {file.filename}")
                
                # Сохраняем в БД
                file_uuid = await self._save_file_to_db(
                    note_id=note_id, file_data=upload_response, category=category
                )
                if not file_uuid:
                    raise RepositoryInternalError(f"No UUID returned for {file.filename}")
                
                uploaded_uuids.append(file_uuid)
            
            logger.info(f"Обработано {len(uploaded_uuids)} файлов категории {category}")
            return uploaded_uuids
            
        except (EmptyFileError, FilesUploadError, FilesHandlingError, RepositoryInternalError):
            raise
        except Exception as e:
            logger.exception(f"Ошибка обработки файлов {category}: {e}")
            raise FilesUploadError from e

    async def get_files_metadata(self, files_uuids: List[str]) -> List[dict]:
        """Получение метаданных файлов по UUID"""
        if not files_uuids:
            return []

        try:
            metadata_list = []
            for file_uuid in files_uuids:
                file_data = await get_file(file_uuid)
                metadata_list.append(file_data)
            logger.info(f"Получены метаданные для {len(metadata_list)} файлов")
            return metadata_list
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Ошибка получения метаданных: {e}")
            raise FilesHandlingError from e
