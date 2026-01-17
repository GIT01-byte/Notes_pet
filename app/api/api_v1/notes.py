from typing import List
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from core.s3_client import s3_client
from core.config import settings
from core.notes_repo import NotesRepo
from core.schemas.notes import NoteCreate, NoteRead

from .service import NoteService
from .deps import NoteCreateForm

router = APIRouter(
    prefix=settings.api.v1.notes,
    tags=["Notes"]
)


@router.post("/create", response_model=NoteRead)
async def create_notes(
    note_create_form: NoteCreateForm = Depends(),
):
    # Загружаем все типы медиа через вспомогательную функцию
    note_service = NoteService()
    
    video_urls = await note_service.upload_media_files(files=note_create_form.video_files, category="videos")  # type: ignore
    image_urls = await note_service.upload_media_files(files=note_create_form.image_files, category="photos")  # type: ignore
    audio_urls = await note_service.upload_media_files(files=note_create_form.audio_files, category="audios")  # type: ignore
    
    # Теперь подготавливаем данные для БД
    note_data = NoteCreate(
        title=note_create_form.title,
        content=note_create_form.content,
        video_urls=video_urls,
        image_urls=image_urls,
        audio_urls=audio_urls,
    )
    
    # Сохраняем в БД 
    new_note = await NotesRepo.create_note(note_data)
    
    return new_note


@router.delete("/delete/{note_id}")
async def delete_note(note_id: int):
    # TODO сделать удаление файлов в S3
    # Удаляем из БД
    await NotesRepo.delete_note(note_id)
    return {"msg": f"Заметка с ID {note_id} успешно удалена"}


@router.get("/get_all", response_model=list[NoteRead])
async def get_notes():
    notes = await NotesRepo.get_all_notes()
    return notes
