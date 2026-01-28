import sqlalchemy.exc
from typing import Sequence, NoReturn

from sqlalchemy import delete, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper, NotesOrm
from core.schemas import NoteCreate, NoteDelete, NoteUpdate

from notes.exceptions.exceptions import (
    DeleteNoteError,
    NoteNotFoundError,
    NoteAlreadyExistsError,
    RepositoryInternalError,
)
from utils.logging import logger


class NotesRepo:
    @staticmethod
    async def get_all_notes() -> Sequence[NotesOrm] | None:
        try:
            async with db_helper.session_factory() as session:
                logger.debug("Попытка получить все заметки")
                
                stmt = select(NotesOrm).order_by(NotesOrm.id)
                result = await session.scalars(stmt)
                
                if result:
                    return result.all()
                
                logger.debug("Заметки не найдены.")
                raise NoteNotFoundError("Заметки не найдены.") from None
        except NoteNotFoundError:
            raise
        except SQLAlchemyError as e:
            logger.exception(f"Ошибка базы данных при получении заметок: {e}")
            raise RepositoryInternalError(
                "Не удалось получить заметки из-за ошибки базы данных."
            ) from e
        except Exception as e:
            logger.exception(f"Неожиданная ошибка при получении заметок: {e}")
            raise RepositoryInternalError(
                "Не удалось получить заметки из-за неожиданной ошибки."
            ) from e

    @staticmethod
    async def get_user_notes(username: str) -> Sequence[NotesOrm] | None:
        try:
            async with db_helper.session_factory() as session:
                logger.debug(f"Попытка получить заметки пользоваетеля {username!r}")

                stmt = (
                    select(NotesOrm)
                    .where(NotesOrm.user == username)
                    .order_by(NotesOrm.id)
                )
                result = await session.scalars(stmt)

                if result:
                    logger.debug(f"Заметки пользоваетеля {username!r} получены.")
                    return result.all()

                logger.debug(f"Заметки пользоваетеля {username!r} не найдены.")
                raise NoteNotFoundError(
                    f"Заметки пользоваетеля {username!r} не найдены."
                ) from None
        except NoteNotFoundError:
            raise
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка базы данных при получении заметок пользоваетеля {username!r}: {e}"
            )
            raise RepositoryInternalError(
                "Не удалось получить заметки пользоваетеля из-за ошибки базы данных."
            ) from e
        except Exception as e:
            logger.exception(
                f"Неожиданная ошибка при получении заметок пользоваетеля {username!r}: {e}"
            )
            raise RepositoryInternalError(
                "Не удалось получить заметки пользоваетеля из-за неожиданной ошибки."
            ) from e

    @staticmethod
    async def get_note(note_id: int, username: str) -> NotesOrm | None:
        try:
            async with db_helper.session_factory() as session:
                logger.debug(
                    f"Попытка получить заметку с ID: {note_id} у пользоваетеля {username!r}"
                )

                stmt = (
                    select(NotesOrm)
                    .where(NotesOrm.id == note_id)
                    .where(NotesOrm.user == username)
                )
                result = await session.scalars(stmt)

                if result:
                    logger.debug(
                        f"Заметка с ID: {note_id} у пользоваетеля {username!r} найдена."
                    )
                    return result.first()

                logger.debug(
                    f"Заметка с ID: {note_id} у пользоваетеля {username!r} не найдена."
                )
                raise NoteNotFoundError(
                    f"Заметка с ID: {note_id} у пользоваетеля {username!r} не найдена."
                ) from None
        except NoteNotFoundError:
            raise
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка базы данных при получении заметки с ID {note_id} пользоваетеля {username!r}: {e}"
            )
            raise RepositoryInternalError(
                f"Не удалось получить заметку с ID {note_id} пользоваетеля из-за ошибки базы данных."
            ) from e
        except Exception as e:
            logger.exception(
                f"Неожиданная ошибка при заметки с ID {note_id} пользоваетеля {username!r}: {e}"
            )
            raise RepositoryInternalError(
                f"Не удалось получить заметку с ID {note_id} пользоваетеля из-за неожиданной ошибки."
            ) from e

    @staticmethod
    async def create_note(note_to_create: NoteCreate) -> NotesOrm | None:
        try:
            async with db_helper.session_factory() as session:
                logger.debug(
                    f"Попытка создание новой заметки: {note_to_create.title!r} у пользоваетеля {note_to_create.user!r}"
                )

                existing_note = await session.scalar(
                    select(NotesOrm).filter(or_(NotesOrm.title == note_to_create.title))
                )
                if existing_note:
                    error_msg = f"Заметка с заголовком: {note_to_create.title!r} уже существует."
                    logger.error(error_msg)
                    raise NoteAlreadyExistsError(error_msg)

                new_note = NotesOrm(**note_to_create.model_dump())
                session.add(new_note)
                await session.commit()
                await session.refresh(new_note)
                logger.info(
                    f"Заметка ID: {new_note.id}, заголовок: {new_note.title!r} успешно создана."
                )
                return new_note
        except NoteAlreadyExistsError:
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

    @staticmethod
    async def delete_user_note(note_to_delete: NoteDelete) -> NoReturn:
        try:
            async with db_helper.session_factory() as session:
                logger.debug(
                    f"Попытка удаления заметки с ID: {note_to_delete.id} у пользоваетеля {note_to_delete.username!r}"
                )

                found_note = await session.scalar(
                    select(NotesOrm)
                    .where(NotesOrm.id == note_to_delete.id)
                    .where(NotesOrm.user == note_to_delete.username)
                )

                if not found_note:
                    logger.debug(
                        f"Заметка с ID: {note_to_delete.id} у пользователя {note_to_delete.username!r} не найдена."
                    )
                    raise NoteNotFoundError(
                        f"Заметка с ID: {note_to_delete.id} у пользователя {note_to_delete.username!r} не найдена."
                    ) from None

                if found_note:
                    await session.delete(found_note)
                    await session.commit()
                    logger.debug(
                        f"Заметка с ID: {note_to_delete.id} у пользователя {note_to_delete.username!r} успешно удалена"
                    )
                raise DeleteNoteError(f"Note with ID {note_to_delete.id} is not delete")
        except NoteNotFoundError:
            raise
        except DeleteNoteError:
            raise
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка базы данных при удалении заметки с ID {note_to_delete.id} пользоваетеля {note_to_delete.username!r}: {e}"
            )
            raise RepositoryInternalError(
                f"Не удалось удалить заметку с ID {note_to_delete.id} пользоваетеля из-за ошибки базы данных."
            ) from e
        except Exception as e:
            logger.exception(
                f"Неожиданная ошибка при удалении заметки с ID {note_to_delete.id} пользоваетеля {note_to_delete.username!r}: {e}"
            )
            raise RepositoryInternalError(
                f"Не удалось удалить заметку с ID {note_to_delete.id} пользоваетеля из-за неожиданной ошибки."
            ) from e
