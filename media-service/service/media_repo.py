from typing import Sequence, NoReturn

from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError

from core.models.db_helper import db_helper

from core.schemas.files import FileMeatadataCreate
from core.models.files import FilesMeatadataOrm

from exceptions.exceptions import (
    DeleteNoteError,
    NoteNotFoundError,
    NoteAlreadyExistsError,
    RepositoryInternalError,
)

from utils.logging import logger

# TODO Доработать
class MediaRepo:
    @staticmethod
    async def create_note(file_metadata_to_create: FileMeatadataCreate) -> FilesMeatadataOrm | None:
        try:
            async with db_helper.session_factory() as session:
                logger.debug(
                    f"Попытка создание новой метадаты: {file_metadata_to_create.filename!r}/{file_metadata_to_create.uplo}"
                )

                existing_metadata = await session.scalar(
                    select(FilesMeatadataOrm)
                    .filter(
                        or_(FilesMeatadataOrm.uuid == file_metadata_to_create.uuid)
                    )
                )
                if existing_metadata:
                    error_msg = f"Метаданные с UUID: {file_metadata_to_create.uuid!r} уже существует."
                    logger.error(error_msg)
                    raise NoteAlreadyExistsError(error_msg)

                new_note = FilesMeatadataOrm(**file_metadata_to_create.model_dump())
                session.add(new_note)
                await session.commit()
                await session.refresh(new_note)
                logger.info(
                    f"Метаданные файла {} ID: {new_note.id}, заголовок: {new_note.title!r} успешно создана."
                )
                return new_note
        except FileMetadataAlreadyExistsError:
            raise
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка базы данных при создании заметки {NoteCreate.title!r}: {e}"
            )
            raise RepositoryInternalError(
                "Не удалось создать заметку из-за ошибки базы данных."
            ) from e
        except Exception as e:
            logger.exception(
                f"Неожиданная ошибка при создании заметки {NoteCreate.title!r}: {e}"
            )
            raise RepositoryInternalError(
                f"Не удалось создать заметку из-за неожиданной ошибки."
            ) from e