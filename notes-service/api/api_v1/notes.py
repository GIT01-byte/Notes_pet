from fastapi import APIRouter, Depends

from core.s3_client import s3_client
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

from .service import NoteService
from .deps import NoteCreateForm, get_current_user

from utils.logging import logger

router = APIRouter(prefix=settings.api.v1.notes, tags=["Notes"])


@router.get("/health_check")
async def health_check():
    return {"success": "Note service started"}


# TODO добавить обработку ошибок связанную с куки
# TODO добавить ограничение обработки файлов макс 200 МБ
@router.post("/create")
async def create_notes(
    note_create_form: NoteCreateForm = Depends(),
    current_user=Depends(get_current_user),
):
    try:
        logger.debug(
            f"Попытка создания новой заметки {note_create_form.title!r} пользователя {current_user.username!r}"
            f"с помощью {settings.api.v1.notes}/create"
        )

        # Загружаем все типы медиа через вспомогательную функцию
        note_service = NoteService()

        video_urls = await note_service.upload_media_files(files=note_create_form.video_files, category="videos")  # type: ignore
        image_urls = await note_service.upload_media_files(files=note_create_form.image_files, category="photos")  # type: ignore
        audio_urls = await note_service.upload_media_files(files=note_create_form.audio_files, category="audios")  # type: ignore

        # Теперь подготавливаем данные для БД
        logger.debug("Подготовка данных для создания заметки в БД...")
        note_data = NoteCreate(
            user=current_user.username,
            title=note_create_form.title,
            content=note_create_form.content,
            video_urls=video_urls,
            image_urls=image_urls,
            audio_urls=audio_urls,
        )

        # Сохраняем в БД
        new_note = await NotesRepo.create_note(note_data)
        if new_note:
            logger.info(f"Создание заметки {new_note.title!r} прошла успешно!")
            return {"message": f"Создание заметки {new_note.title!r} прошла успешно!"}

        raise NoteCreateFailedError
    except FilesHandlingError:
        raise
    except FilesUploadError:
        raise
    except NoteAlreadyExistsError:
        raise
    except NoteCreateFailedError:
        logger.exception("Создание заметки не удалось!")
        raise


@router.delete("/delete/{note_id}")
async def delete_note(
    note_id: int,
    current_user=Depends(get_current_user),
):
    try:
        logger.debug(
            f"Попытка удаления заметки ID {note_id} пользователя {current_user.username!r}"
            f"с помощью {settings.api.v1.notes}/delete/{note_id}"
        )

        # Удаление медиа-файлов из S3
        note = await NotesRepo.get_note(note_id=note_id, username=current_user.username)
        if note:
            await s3_client.delete_files(note.video_urls)
            await s3_client.delete_files(note.image_urls)
            await s3_client.delete_files(note.audio_urls)
        else:
            raise NoteNotFoundError

        # Удаляем из БД
        delete_result = await NotesRepo.delete_note(note)
        if delete_result is None:
            logger.info(f"Заметка с ID {note_id} успешно удалена")
            return {"message": f"Заметка с ID {note_id} успешно удалена"}

        raise NoteDeleteFailedError
    except NoteNotFoundError:
        raise
    except NoteDeleteFailedError:
        logger.exception("Удаление заметки не удалось!")
        raise


@router.get("/get_all_user_notes/")
async def get_all_user_notes(current_user=Depends(get_current_user)):
    try:
        logger.debug(
            f"Получение всех заметок пользователя {current_user.username!r}"
            f"с помощью {settings.api.v1.notes}/get_all_user_notes/"
        )

        notes = await NotesRepo.get_user_notes(current_user.username)

        if notes:
            logger.info(
                f"Получение заметок пользователя {current_user.username!r} прошло успешно!"
            )
            return {"data": notes}

        raise NoteNotFoundError
    except NoteNotFoundError:
        logger.info("Заметки пользователя не найдены либо их нет!")
        return {"data": []}


@router.get("/get_user_note/{note_id}")
async def get_user_note(
    note_id: int,
    current_user=Depends(get_current_user),
):
    try:
        logger.debug(
            f"Получение заметки ID {note_id} пользователя {current_user.username!r}"
            f"с помощью {settings.api.v1.notes}/get_user_note/{note_id}"
        )

        note = await NotesRepo.get_note(note_id=note_id, username=current_user.username)

        if note:
            logger.info(f"Получение заметки ID {note_id} прошло успешно!")
            return {"data": note}

        raise NoteNotFoundError
    except NoteNotFoundError:
        logger.exception("Заметка не найдена!")
        raise


# TODO сделать доступ тролько для админа
@router.get("/get_all/")
async def get_notes():
    try:
        logger.debug(
            f"Получение всех заметок с помощью {settings.api.v1.notes}/get_all/"
        )

        notes = await NotesRepo.get_all_notes()

        if notes:
            logger.info("Получение заметок прошло успешно!")
            return {"data": notes}

        raise NoteNotFoundError
    except NoteNotFoundError:
        logger.exception("Заметки не найдены!")
        raise
