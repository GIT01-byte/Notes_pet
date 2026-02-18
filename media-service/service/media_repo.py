from uuid import UUID

from sqlalchemy import select, or_
from sqlalchemy.exc import SQLAlchemyError

from core.models.db_helper import db_helper

from core.schemas.files import FileMeatadataCreate
from core.models.files import FilesMetadataOrm

from exceptions.exceptions import (
    DataConflictError,
    EntityNotFoundError,
    RepositoryInternalError,
)

from utils.logging import logger


class MediaRepo:
    @staticmethod
    async def create_metadata(file_metadata_to_create: FileMeatadataCreate) -> FilesMetadataOrm | None:
        try:
            async with db_helper.session_factory() as session:
                logger.debug(
                    f"Попытка создания новых метаданных: {file_metadata_to_create.s3_url!r}"
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
                    raise DataConflictError(error_msg)

                new_note = FilesMetadataOrm(**file_metadata_to_create.model_dump())
                session.add(new_note)
                await session.commit()
                await session.refresh(new_note)
                logger.info(
                    f"Метаданные файла {file_metadata_to_create.filename!r} "
                    f"ID: {file_metadata_to_create.uuid}, S3 URL: {file_metadata_to_create.s3_url!r} успешно созданы."
                )
                return new_note
        except DataConflictError:
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
                "Не удалось создать метаданные из-за неожиданной ошибки."
            ) from e
    
    @staticmethod
    async def get_files_metadata(file_uuid: UUID) -> FilesMetadataOrm | None:
        try:
            async with db_helper.session_factory() as session:
                logger.debug(f"Попытка получения метаданных файла с UUID: {file_uuid}")

                stmt = (
                    select(FilesMetadataOrm)
                    .where(FilesMetadataOrm.uuid == file_uuid)
                    .order_by(FilesMetadataOrm.id)
                )
                result = await session.scalars(stmt)
                metadata = result.first()

                if metadata:
                    logger.info(f"Метаданные файла с UUID: {file_uuid} успешно получены.")
                    return metadata

                logger.warning(f"Метаданные файла с UUID: {file_uuid} не найдены.")
                raise EntityNotFoundError(
                    f"Метаданные файла с UUID: {file_uuid} не найдены."
                )
        except EntityNotFoundError:
            raise
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка базы данных при получении метаданных файла с UUID {file_uuid}: {e}"
            )
            raise RepositoryInternalError(
                f"Не удалось получить метаданные файла с UUID {file_uuid} из-за ошибки базы данных."
            ) from e
        except Exception as e:
            logger.exception(
                f"Неожиданная ошибка при получении метаданных файла с UUID {file_uuid}: {e}"
            )
            raise RepositoryInternalError(
                f"Не удалось получить метаданные файла с UUID {file_uuid} из-за неожиданной ошибки."
            ) from e
    
    @staticmethod
    async def delete_file_metadata(file_metadata_obj: FilesMetadataOrm ) -> None:
        try:
            async with db_helper.session_factory() as session:
                logger.debug(f"Попытка удаления метаданных файла с UUID: {file_metadata_obj.uuid}")
                
                await session.delete(file_metadata_obj)
                await session.commit()
                
                logger.info(f"Метаданные файла с UUID: {file_metadata_obj.uuid} успешно удалены.")
        except EntityNotFoundError:
            raise
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка базы данных при удалении метаданных файла с UUID {file_metadata_obj.uuid}: {e}"
            )
            raise RepositoryInternalError(
                f"Не удалось удалить метаданные файла с UUID {file_metadata_obj.uuid} из-за ошибки базы данных."
            ) from e
        except Exception as e:
            logger.exception(
                f"Неожиданная ошибка при удалении метаданных файла с UUID {file_metadata_obj.uuid}: {e}"
            )
            raise RepositoryInternalError(
                f"Не удалось удалить метаданные файла с UUID {file_metadata_obj.uuid} из-за неожиданной ошибки."
            ) from e
