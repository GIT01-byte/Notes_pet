from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError

from core.models.notes import VideoFilesOrm, ImageFilesOrm, AudioFilesOrm
from core.models.db_helper import db_helper
from integrations.files.schemas import NSFileUploadResponse
from exceptions.exceptions import RepositoryInternalError
from utils.logging import logger


class MediaFilesRepo:
    @staticmethod
    async def add_video(
        note_id: int, file_data: NSFileUploadResponse
    ) -> VideoFilesOrm | None:
        try:
            async with db_helper.session_factory() as session:
                logger.debug(
                    f"Попытка добавления видео {file_data.uuid} к заметке {note_id}"
                )

                video = VideoFilesOrm(
                    note_id=note_id,
                    uuid=UUID(file_data.uuid),
                    s3_url=file_data.s3_url,
                    content_type=file_data.content_type,
                    category=file_data.category,
                    uploaded_at_s3=file_data.uploaded_at_s3,
                )
                session.add(video)
                await session.commit()
                await session.refresh(video)
                logger.info(
                    f"Видео {file_data.uuid} успешно добавлено к заметке {note_id}"
                )
                return video
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка базы данных при добавлении видео {file_data.uuid}: {e}"
            )
            raise RepositoryInternalError(
                "Не удалось добавить видео из-за ошибки базы данных."
            ) from e
        except Exception as e:
            logger.exception(
                f"Неожиданная ошибка при добавлении видео {file_data.uuid}: {e}"
            )
            raise RepositoryInternalError(
                "Не удалось добавить видео из-за неожиданной ошибки."
            ) from e

    @staticmethod
    async def add_image(
        note_id: int, file_data: NSFileUploadResponse
    ) -> ImageFilesOrm | None:
        try:
            async with db_helper.session_factory() as session:
                logger.debug(
                    f"Попытка добавления изображения {file_data.uuid} к заметке {note_id}"
                )

                image = ImageFilesOrm(
                    note_id=note_id,
                    uuid=UUID(file_data.uuid),
                    s3_url=file_data.s3_url,
                    content_type=file_data.content_type,
                    category=file_data.category,
                    uploaded_at_s3=file_data.uploaded_at_s3,
                )
                session.add(image)
                await session.commit()
                await session.refresh(image)
                logger.info(
                    f"Изображение {file_data.uuid} успешно добавлено к заметке {note_id}"
                )
                return image
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка базы данных при добавлении изображения {file_data.uuid}: {e}"
            )
            raise RepositoryInternalError(
                "Не удалось добавить изображение из-за ошибки базы данных."
            ) from e
        except Exception as e:
            logger.exception(
                f"Неожиданная ошибка при добавлении изображения {file_data.uuid}: {e}"
            )
            raise RepositoryInternalError(
                "Не удалось добавить изображение из-за неожиданной ошибки."
            ) from e

    @staticmethod
    async def add_audio(
        note_id: int, file_data: NSFileUploadResponse
    ) -> AudioFilesOrm | None:
        try:
            async with db_helper.session_factory() as session:
                logger.debug(
                    f"Попытка добавления аудио {file_data.uuid} к заметке {note_id}"
                )

                audio = AudioFilesOrm(
                    note_id=note_id,
                    uuid=UUID(file_data.uuid),
                    s3_url=file_data.s3_url,
                    content_type=file_data.content_type,
                    category=file_data.category,
                    uploaded_at_s3=file_data.uploaded_at_s3,
                )
                session.add(audio)
                await session.commit()
                await session.refresh(audio)
                logger.info(
                    f"Аудио {file_data.uuid} успешно добавлено к заметке {note_id}"
                )
                return audio
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка базы данных при добавлении аудио {file_data.uuid}: {e}"
            )
            raise RepositoryInternalError(
                "Не удалось добавить аудио из-за ошибки базы данных."
            ) from e
        except Exception as e:
            logger.exception(
                f"Неожиданная ошибка при добавлении аудио {file_data.uuid}: {e}"
            )
            raise RepositoryInternalError(
                "Не удалось добавить аудио из-за неожиданной ошибки."
            ) from e
