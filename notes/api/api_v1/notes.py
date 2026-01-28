from fastapi import APIRouter, Depends, HTTPException, status

from core.s3_client import s3_client
from core.config import settings
from core.notes_repo import NotesRepo
from core.schemas import NoteCreate, NoteRead
from notes.core.schemas.notes import NoteDelete

from .service import NoteService
from .deps import NoteCreateForm, get_current_user

router = APIRouter(
    prefix=settings.api.v1.notes,
    tags=["Notes"]
)


@router.get("/health_check")
async def health_check():
    return {"success": "Note service started"}

# TODO добавить обработку ошибок (уже имеющиеся заметки, не валидыне данные)
@router.post("/create")
async def create_notes(
    note_create_form: NoteCreateForm = Depends(),
    current_user = Depends(get_current_user),
):
    try:
        # Загружаем все типы медиа через вспомогательную функцию
        note_service = NoteService()
        
        video_urls = await note_service.upload_media_files(files=note_create_form.video_files, category="videos")  # type: ignore
        image_urls = await note_service.upload_media_files(files=note_create_form.image_files, category="photos")  # type: ignore
        audio_urls = await note_service.upload_media_files(files=note_create_form.audio_files, category="audios")  # type: ignore
        
        # Теперь подготавливаем данные для БД
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
            return {"message": f"Создание заметки {new_note.title!r} прошла успешно!"}
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Note create failed"
        )

    except Exception as e:
        print(f"EXC:    exception in notes/create endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Note create failed"
        )


@router.delete("/delete/{note_id}")
async def delete_note(
    note_id: int,
    current_user = Depends(get_current_user),
):
    try:
        # Удаление медиа-файлов из S3
        note = await NotesRepo.get_note(note_id=note_id, username=current_user.username)
        if note:
            await s3_client.delete_files(note.video_urls)
            await s3_client.delete_files(note.image_urls)
            await s3_client.delete_files(note.audio_urls)
        else:
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Заметка не найдена",
            )
        
        # Подгатавливаем данные для БД
        note_delete_data = NoteDelete(
            id=note_id,
            username=current_user.username
        )
        # Удаляем из БД
        await NotesRepo.delete_user_note(note_delete_data)
        
        return {"message": f"Заметка с ID {note_id} успешно удалена"}
    
    except Exception as e:
        print(f"EXC:    exception in notes/delete endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Note delete failed"
        )


@router.get("/get_all_user_notes/")
async def get_all_user_notes(current_user = Depends(get_current_user)):
    notes = await NotesRepo.get_user_notes(current_user.username)
    
    return {"data": notes}


@router.get("/get_user_note/{note_id}")
async def get_user_note(
    note_id: int,
    current_user = Depends(get_current_user),
):
    note = await NotesRepo.get_note(note_id=note_id, username=current_user.username)
    
    return {"data": note}


# TODO сделать доступ тролько для админа
@router.get("/get_all")
async def get_notes():
    notes = await NotesRepo.get_all_notes()
    
    return {"data": notes}
