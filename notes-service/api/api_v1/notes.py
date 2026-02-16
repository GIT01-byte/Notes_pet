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
from .deps import NoteCreateForm

from integrations.auth import get_current_user

from utils.logging import logger
import uuid

router = APIRouter(prefix=settings.api.v1.notes, tags=["Notes"])


@router.get("/health_check")
async def health_check():
    return {"success": "Note service started"}


# TODO добавить обработку ошибок связанную с куки
# TODO добавить модуль для взаимодействия с миросервисом файлов
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

        # FIXME переделать логику отправки файлов на логику взаимодествия с микросеврисом файлов (media service)
        # Загружаем все типы медиа через вспомогательную функцию 
        note_service = NoteService()
        
        new_note_uuid = str(uuid.uuid4())

        video_uuids = await note_service.upload_media_files(files=note_create_form.video_files, category="videos", note_uuid=new_note_uuid)  
        image_uuids = await note_service.upload_media_files(files=note_create_form.image_files, category="images", note_uuid=new_note_uuid) 
        audio_uuids = await note_service.upload_media_files(files=note_create_form.audio_files, category="audios", note_uuid=new_note_uuid)

        # Теперь подготавливаем данные для БД
        logger.debug("Подготовка данных для создания заметки в БД...")
        note_data = NoteCreate(
            user=current_user.username,
            title=note_create_form.title,
            content=note_create_form.content,
            video_uuid=video_uuids,
            image_uuid=image_uuids,
            audio_uuid=audio_uuids,
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
             # FIXME
            await s3_client.delete_files(note.video_uuid)
            await s3_client.delete_files(note.image_uuid)
            await s3_client.delete_files(note.audio_uuid)
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
