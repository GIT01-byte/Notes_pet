from typing import List
from uuid import UUID

from fastapi import HTTPException, UploadFile

from core.models.notes import NotesOrm
from core.media_files_repo import MediaFilesRepo

from exceptions.exceptions import (
    EmptyFileError,
    FilesDeleteError,
    FilesHandlingError,
    FilesUploadError,
    RepositoryInternalError,
)

from integrations.files.files import MS_delete_file, MS_get_file, MS_upload_file
from integrations.files.schemas import (
    NSFileUploadRequest,
    NSFileUploadResponse,
)
from integrations.files.constants import (
    VIDEO_FILES_NAME,
    IMAGE_FILES_NAME,
    AUDIO_FILES_NAME,
)

from utils.logging import logger


class NoteService:
    async def _upload_media_file(
        self, file: UploadFile, entity_id: int
    ) -> NSFileUploadResponse:
        """Загрузка файла в S3 через Media service"""
        try:
            request = NSFileUploadRequest(
                upload_context="post_attachment", file=file, entity_id=entity_id
            )
            response = await MS_upload_file(request)
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
        self, note_id: int, file_data: NSFileUploadResponse, category: str
    ) -> UUID:
        """Сохранение метаданных файла в БД"""
        try:
            match category:
                case category if category == VIDEO_FILES_NAME:
                    result = await MediaFilesRepo.add_video(
                        note_id=note_id, file_data=file_data
                    )
                case category if category == IMAGE_FILES_NAME:
                    result = await MediaFilesRepo.add_image(
                        note_id=note_id, file_data=file_data
                    )
                case category if category == AUDIO_FILES_NAME:
                    result = await MediaFilesRepo.add_audio(
                        note_id=note_id, file_data=file_data
                    )
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

            logger.info(
                f"Обработка {len(files)} файлов категории {category} для заметки {note_id}"
            )

            uploaded_uuids: list[UUID] = []
            for file in files:
                # Загружаем в S3
                upload_response = await self._upload_media_file(
                    file=file, entity_id=note_id
                )
                if not upload_response:
                    raise FilesUploadError(f"No upload response for {file.filename}")

                # Сохраняем в БД
                file_uuid = await self._save_file_to_db(
                    note_id=note_id, file_data=upload_response, category=category
                )
                if not file_uuid:
                    raise RepositoryInternalError(
                        f"No UUID returned for {file.filename}"
                    )

                uploaded_uuids.append(file_uuid)

            logger.info(f"Обработано {len(uploaded_uuids)} файлов категории {category}")
            return uploaded_uuids

        except (
            EmptyFileError,
            FilesUploadError,
            FilesHandlingError,
            RepositoryInternalError,
        ):
            raise
        except Exception as e:
            logger.exception(f"Ошибка обработки файлов {category}: {e}")
            raise FilesUploadError from e

    async def _delete_media_file(self, file_uuid: str):
        """Удаление файла в S3 через Media service"""
        try:
            response = await MS_delete_file(file_uuid)
            if not response:
                raise FilesDeleteError(f"No response for file UUID: {file_uuid}")
            logger.info(f"Файл {file_uuid} удален из S3")
            return response
        except (HTTPException, FilesDeleteError):
            raise
        except Exception as e:
            logger.exception(f"Ошибка удаления файла {file_uuid}: {e}")
            raise FilesDeleteError from e

    async def delete_media_files_from_s3(self, note: NotesOrm):
        """Удаление всех медиафайлов заметки из S3"""
        try:
            total_files = len(note.video_files) + len(note.image_files) + len(note.audio_files)
            if total_files == 0:
                logger.info(f"Заметка {note.id} не содержит медиафайлов")
                return {"ok": True, "message": "No media files to delete"}

            logger.info(f"Удаление {total_files} медиафайлов заметки {note.id}")
            deleted_count = 0
            failed_uuids = []

            for video_file in note.video_files:
                try:
                    await self._delete_media_file(file_uuid=str(video_file.uuid))
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Не удалось удалить видео {video_file.uuid}: {e}")
                    failed_uuids.append(str(video_file.uuid))

            for image_file in note.image_files:
                try:
                    await self._delete_media_file(file_uuid=str(image_file.uuid))
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Не удалось удалить изображение {image_file.uuid}: {e}")
                    failed_uuids.append(str(image_file.uuid))

            for audio_file in note.audio_files:
                try:
                    await self._delete_media_file(file_uuid=str(audio_file.uuid))
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Не удалось удалить аудио {audio_file.uuid}: {e}")
                    failed_uuids.append(str(audio_file.uuid))

            if failed_uuids:
                logger.warning(f"Удалено {deleted_count}/{total_files} файлов. Ошибки: {failed_uuids}")
                raise FilesDeleteError(f"Failed to delete {len(failed_uuids)} files: {failed_uuids}")

            logger.info(f"Все {deleted_count} медиафайлов заметки {note.id} удалены")
            return {"ok": True, "message": f"Deleted {deleted_count} media files"}

        except FilesDeleteError:
            raise
        except Exception as e:
            logger.exception(f"Ошибка удаления медиафайлов заметки {note.id}: {e}")
            raise FilesDeleteError from e
