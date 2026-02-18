from sys import exc_info
from uuid import UUID
from fastapi import APIRouter, Depends

from core.config import settings
from core.notes_repo import NotesRepo
from core.schemas import NoteCreate

from exceptions.exceptions import (
    FilesHandlingError,
    FilesUploadError,
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


@router.get("/health_check")
async def health_check():
    return {"success": "Note service started"}


# TODO добавить обработку ошибок связанную с куки
# TODO передалть механизм сохранения медиа-файлов в БД через отдельные таблицы и relationship`ы
@router.post("/create")
async def create_notes(
    note_create_form: NoteCreateForm = Depends(),
    note_media_files: NoteCreateMediaFilesForm = Depends(),
    current_user=Depends(get_current_user),
):
    try:
        logger.info(f"Создание заметки '{note_create_form.title}' пользователем {current_user.username}")

        note_service = NoteService()

        # Создаем заметку без медиафайлов
        note_data = NoteCreate(
            user=current_user.username,
            title=note_create_form.title,
            content=note_create_form.content,
        )

        new_note = await NotesRepo.create_note(note_data)
        if not new_note:
            raise NoteCreateFailedError

        # Если нет медиафайлов - возвращаем результат
        if not note_media_files.video_files and not note_media_files.image_files and not note_media_files.audio_files:
            logger.info(f"Заметка {new_note.id} создана без медиафайлов")
            return {"message": f"Заметка '{new_note.title}' создана без медиафайлов"}

        # Обрабатываем медиафайлы
        uploaded_files_uuids = {}
        
        if note_media_files.video_files:
            video_uuids = await note_service.process_media_files(
                files=note_media_files.video_files,
                category=VIDEO_FILES_NAME,
                note_id=int(new_note.id),
            )
            uploaded_files_uuids["video"] = video_uuids

        if note_media_files.image_files:
            image_uuids = await note_service.process_media_files(
                files=note_media_files.image_files,
                category=IMAGE_FILES_NAME,
                note_id=int(new_note.id),
            )
            uploaded_files_uuids["image"] = image_uuids

        if note_media_files.audio_files:
            audio_uuids = await note_service.process_media_files(
                files=note_media_files.audio_files,
                category=AUDIO_FILES_NAME,
                note_id=int(new_note.id),
            )
            uploaded_files_uuids["audio"] = audio_uuids

        logger.info(f"Заметка {new_note.id} создана с медиафайлами")
        return {
            "message": f"Заметка '{new_note.title}' успешно создана",
            "note_id": new_note.id,
            "uploaded_files": uploaded_files_uuids
        }

    except (FilesHandlingError, FilesUploadError, NoteAlreadyExistsError, NoteCreateFailedError):
        raise
    except Exception as e:
        logger.exception(f"Ошибка создания заметки: {e}")
        raise NoteCreateFailedError


@router.delete("/delete/{note_id}")
async def delete_note(
    note_id: int,
    current_user=Depends(get_current_user),
):
    try:
        logger.info(f"Удаление заметки {note_id} пользователем {current_user.username}")

        note = await NotesRepo.get_note(note_id=note_id, username=current_user.username)
        if not note:
            raise NoteNotFoundError

        await NotesRepo.delete_note(note)
        logger.info(f"Заметка {note_id} успешно удалена")
        return {"message": f"Заметка {note_id} успешно удалена"}

    except (NoteNotFoundError, NoteDeleteFailedError):
        raise
    except Exception as e:
        logger.exception(f"Ошибка удаления заметки {note_id}: {e}")
        raise NoteDeleteFailedError


@router.get("/get_all_user_notes/")
async def get_all_user_notes(current_user=Depends(get_current_user)):
    try:
        notes = await NotesRepo.get_user_notes(current_user.username)
        if notes:
            logger.info(f"Получено {len(notes)} заметок пользователя {current_user.username}")
            return {"data": notes}
        return {"data": []}
    except NoteNotFoundError:
        return {"data": []}
    except Exception as e:
        logger.exception(f"Ошибка получения заметок: {e}")
        return {"data": []}


@router.get("/get_user_note/{note_id}")
async def get_user_note(
    note_id: int,
    current_user=Depends(get_current_user),
):
    try:
        note = await NotesRepo.get_note(note_id=note_id, username=current_user.username)
        if not note:
            raise NoteNotFoundError
        logger.info(f"Получена заметка {note_id}")
        return {"data": note}
    except NoteNotFoundError:
        raise
    except Exception as e:
        logger.exception(f"Ошибка получения заметки {note_id}: {e}")
        raise NoteNotFoundError


@router.get("/get_all/")
async def get_notes():
    try:
        notes = await NotesRepo.get_all_notes()
        if notes:
            logger.info(f"Получено {len(notes)} заметок")
            return {"data": notes}
        raise NoteNotFoundError
    except NoteNotFoundError:
        raise
    except Exception as e:
        logger.exception(f"Ошибка получения всех заметок: {e}")
        raise NoteNotFoundError
