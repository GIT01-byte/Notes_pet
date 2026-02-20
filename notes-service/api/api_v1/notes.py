
from fastapi import APIRouter, Depends

from core.config import settings
from core.notes_repo import NotesRepo
from core.schemas import NoteCreate

from exceptions.exceptions import (
    FilesHandlingError,
    FilesUploadError,
    FilesDeleteError,
    NoteNotFoundError,
    NoteAlreadyExistsError,
    NoteCreateFailedError,
    NoteDeleteFailedError,
)

from integrations.files.constants import (
    VIDEO_FILES_NAME,
    AUDIO_FILES_NAME,
    IMAGE_FILES_NAME,
)

from .service import NoteService
from .deps import NoteCreateForm, NoteCreateMediaFilesForm

from integrations.auth.auth import get_current_user

from utils.logging import logger

router = APIRouter(prefix=settings.api.v1.notes, tags=["Notes"])


# Проверка работоспособности сервиса
@router.get("/health_check")
async def health_check():
    return {"success": "Note service started"}


# TODO добавить обработку ошибок связанную с куки
# TODO вынести лишную логику в сервис
# Создание новой заметки в БД с медиафайлами
@router.post("/create")
async def create_notes(
    note_create_form: NoteCreateForm = Depends(),
    note_media_files: NoteCreateMediaFilesForm = Depends(),
    current_user=Depends(get_current_user),
):
    new_note = None
    try:
        logger.info(
            f"Создание заметки '{note_create_form.title}' пользователем {current_user.username}"
        )

        note_service = NoteService()

        # Создаем заметку без медиафайлов
        note_data = NoteCreate(
            user=current_user.username,
            title=note_create_form.title,
            content=note_create_form.content,
        )

        new_note = await NotesRepo.create_note(note_data)
        if not new_note:
            raise NoteCreateFailedError("Не удалось создать заметку в БД")

        # Если нет медиафайлов - возвращаем результат
        if (
            not note_media_files.video_files
            and not note_media_files.image_files
            and not note_media_files.audio_files
        ):
            logger.info(f"Заметка {new_note.id} создана без медиафайлов")
            return {
                "message": f"Заметка '{new_note.title}' создана без медиафайлов",
                "note_id": new_note.id,
            }

        # Обрабатываем медиафайлы
        uploaded_files_uuids = {}

        if note_media_files.video_files:
            try:
                video_uuids = await note_service.process_media_files(
                    files=note_media_files.video_files,
                    category=VIDEO_FILES_NAME,
                    note_id=int(new_note.id),
                )
                uploaded_files_uuids["video"] = video_uuids
                logger.info(
                    f"Загружено {len(video_uuids)} видео для заметки {new_note.id}"
                )
            except Exception as e:
                logger.error(f"Ошибка загрузки видео для заметки {new_note.id}: {e}")
                raise

        if note_media_files.image_files:
            try:
                image_uuids = await note_service.process_media_files(
                    files=note_media_files.image_files,
                    category=IMAGE_FILES_NAME,
                    note_id=int(new_note.id),
                )
                uploaded_files_uuids["image"] = image_uuids
                logger.info(
                    f"Загружено {len(image_uuids)} изображений для заметки {new_note.id}"
                )
            except Exception as e:
                logger.error(
                    f"Ошибка загрузки изображений для заметки {new_note.id}: {e}"
                )
                raise

        if note_media_files.audio_files:
            try:
                audio_uuids = await note_service.process_media_files(
                    files=note_media_files.audio_files,
                    category=AUDIO_FILES_NAME,
                    note_id=int(new_note.id),
                )
                uploaded_files_uuids["audio"] = audio_uuids
                logger.info(
                    f"Загружено {len(audio_uuids)} аудио для заметки {new_note.id}"
                )
            except Exception as e:
                logger.error(f"Ошибка загрузки аудио для заметки {new_note.id}: {e}")
                raise

        logger.info(
            f"Заметка {new_note.id} создана с {sum(len(v) for v in uploaded_files_uuids.values())} медиафайлами"
        )
        return {
            "message": f"Заметка '{new_note.title}' успешно создана",
            "note_id": new_note.id,
            "uploaded_files": uploaded_files_uuids,
        }

    except (
        FilesHandlingError,
        FilesUploadError,
        NoteAlreadyExistsError,
        NoteCreateFailedError,
    ):
        if new_note:
            logger.error(
                f"Откат: удаление заметки {new_note.id} из-за ошибки загрузки файлов"
            )
            await NotesRepo.delete_note(new_note)
        raise
    except Exception as e:
        logger.exception(
            f"Неожиданная ошибка создания заметки '{note_create_form.title}': {e}"
        )
        if new_note:
            logger.error(f"Заметка {new_note.id} создана, но возникла ошибка")
        raise NoteCreateFailedError from e


# Удаление заметки из БД и S3
@router.delete("/delete/{note_id}")
async def delete_note(
    note_id: int,
    current_user=Depends(get_current_user),
):
    try:
        logger.info(f"Удаление заметки {note_id} пользователем {current_user.username}")

        note_service = NoteService()

        # Проверяем существует ли заметка
        note = await NotesRepo.get_note(note_id=note_id, username=current_user.username)
        if not note:
            logger.warning(
                f"Заметка {note_id} не найдена для пользователя {current_user.username}"
            )
            raise NoteNotFoundError(f"Заметка {note_id} не найдена")

        # Удаляем файлы из S3
        if note.video_files or note.image_files or note.audio_files:
            try:
                delete_status = await note_service.delete_media_files_from_s3(note)
                if not delete_status.get("ok"):
                    logger.error(f"Ошибка при удалении медиафайлов заметки {note_id}")
                    raise FilesDeleteError("Не удалось удалить медиафайлы")
                logger.info(
                    f"{delete_status.get('message', 'Медиафайлы удалены')} для заметки {note_id}"
                )
            except FilesDeleteError:
                raise
            except Exception as e:
                logger.exception(
                    f"Неожиданная ошибка удаления медиафайлов заметки {note_id}: {e}"
                )
                raise FilesDeleteError from e
        else:
            logger.info(f"Заметка {note_id} не содержит медиафайлов")

        # Удаляем заметку из БД
        try:
            await NotesRepo.delete_note(note)
            logger.info(f"Заметка {note_id} успешно удалена из БД")
        except Exception as e:
            logger.exception(f"Ошибка удаления заметки {note_id} из БД: {e}")
            raise NoteDeleteFailedError from e

        return {"message": f"Заметка {note_id} успешно удалена"}

    except (NoteNotFoundError, NoteDeleteFailedError, FilesDeleteError):
        raise
    except Exception as e:
        logger.exception(f"Неожиданная ошибка удаления заметки {note_id}: {e}")
        raise NoteDeleteFailedError from e


# Получение всех заметок пользователя из БД
@router.get("/get_all_user_notes/")
async def get_all_user_notes(current_user=Depends(get_current_user)):
    try:
        logger.info(f"Запрос всех заметок пользователя {current_user.username}")

        notes = await NotesRepo.get_user_notes(current_user.username)
        if notes:
            logger.info(
                f"Получено {len(notes)} заметок пользователя {current_user.username}"
            )
            return {"data": notes}

        logger.info(f"У пользователя {current_user.username} нет заметок")
        return {"data": []}
    except NoteNotFoundError:
        return {"data": []}
    except Exception as e:
        logger.exception(f"Ошибка получения заметок: {e}")
        return {"data": []}


# Получение заметки по id из БД
@router.get("/get_user_note/{note_id}")
async def get_user_note(
    note_id: int,
    current_user=Depends(get_current_user),
):
    try:
        logger.info(f"Запрос заметки {note_id} пользователем {current_user.username}")

        note = await NotesRepo.get_note(note_id=note_id, username=current_user.username)
        if not note:
            logger.warning(
                f"Заметка {note_id} не найдена для пользователя {current_user.username}"
            )
            raise NoteNotFoundError(f"Заметка {note_id} не найдена")

        logger.info(f"Заметка {note_id} успешно получена")
        return {"data": note}
    except NoteNotFoundError:
        raise
    except Exception as e:
        logger.exception(f"Ошибка получения заметки {note_id}: {e}")
        raise NoteNotFoundError from e


# TODO добавить доступом только по правам админа
# Получение всех заметок из БД
@router.get("/get_all/")
async def get_notes():
    try:
        logger.info("Запрос всех заметок")

        notes = await NotesRepo.get_all_notes()
        if notes:
            logger.info(f"Получено {len(notes)} заметок")
            return {"data": notes}

        logger.info("Нет заметок для отображения")
        return {"data": []}
    except NoteNotFoundError:
        return {"data": []}
    except Exception as e:
        logger.exception(f"Ошибка получения всех заметок: {e}")
        return {"data": []}
