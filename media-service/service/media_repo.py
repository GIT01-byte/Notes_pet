from typing import Sequence, NoReturn

from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError

from core.models.db_helper import db_helper

from core.schemas.files import FileMeatadataCreate
from core.models.files import FilesMetadataOrm

from exceptions.exceptions import (
    FileMetadataAlreadyExistsError,
    RepositoryInternalError,
)

from utils.logging import logger

# TODO Доработать
class MediaRepo:
    @staticmethod
    async def create_note(file_metadata_to_create: FileMeatadataCreate) -> FilesMetadataOrm | None:
        try:
            async with db_helper.session_factory() as session:
                logger.debug(
                    f"Попытка создание новой метадаты: {file_metadata_to_create.s3_url!r}"
                )

                existing_metadata = await session.scalar(
                    select(FilesMetadataOrm)
                    .filter(
                        or_(FilesMetadataOrm.uuid == file_metadata_to_create.uuid)
                    )
                )
                if existing_metadata:
                    error_msg = f"Метаданные с UUID: {file_metadata_to_create.uuid!r} уже существуют."
                    logger.error(error_msg)
                    raise FileMetadataAlreadyExistsError(error_msg)

                new_note = FilesMetadataOrm(**file_metadata_to_create.model_dump())
                session.add(new_note)
                await session.commit()
                await session.refresh(new_note)
                logger.info(
                    f"Метаданные файла {file_metadata_to_create.filename!r}\
                        ID: {file_metadata_to_create.uuid}, s3 url: {file_metadata_to_create.s3_url!r} успешно создана."
                )
                return new_note
        except FileMetadataAlreadyExistsError:
            raise
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка базы данных при создании метаданных {file_metadata_to_create.filename!r}: {e}"
            )
            raise RepositoryInternalError(
                "Не удалось создать метаданные из-за ошибки базы данных."
            ) from e
        except Exception as e:
            logger.exception(
                f"Неожиданная ошибка при создании метаданных {file_metadata_to_create.filename!r}: {e}"
            )
            raise RepositoryInternalError(
                f"Не удалось создать метаданные из-за неожиданной ошибки."
            ) from e