from fastapi import APIRouter, Depends, HTTPException, status

from core.s3_client import s3_client
from core.config import settings
from core.notes_repo import NotesRepo
from core.schemas import NoteCreate, NoteRead

from .service import NoteService
from .deps import NoteCreateForm, get_current_user

router = APIRouter(
    prefix=settings.api.v1.notes,
    tags=["Notes"]
)


@router.get("/health_check")
async def health_check():
    return {"success": "Note service started"}


# @router.post("/login")
# async def login_note(request: LoginRequest):
#     async with httpx.AsyncClient() as client:
#         req_data = {
#             "username": request.username, 
#             "password": request.password,
#         }

#         try:
#             login_response = await client.post(
#                 "http://krakend:8080/users/login/", 
#                 data=req_data,
#                 follow_redirects=True,
#             )
            
#             if login_response.status_code != 200:
#                 raise HTTPException(
#                     status_code=status.HTTP_401_UNAUTHORIZED, 
#                     detail=f"Authorization failed: {login_response.text}"
#                 )

#             response_data = login_response.json()
            
#             return {"message": f"Добро пожаловать. Токен: {response_data['access_token']}"}
            
#         except httpx.RequestError as exc:
#             raise HTTPException(status_code=503, detail=f"Gateway unavailable: {exc}")
        

@router.post("/create", response_model=NoteRead)
async def create_notes(
    note_create_form: NoteCreateForm = Depends(),
    current_user = Depends(get_current_user),
):
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
    
    return new_note


@router.delete("/delete/{note_id}")
async def delete_note(
    note_id: int,
    current_user = Depends(get_current_user),
    ):
    # Удаление медиа-файлов из S3
    note = await NotesRepo.get_note(note_id)
    if note:
        await s3_client.delete_files(note.video_urls)
        await s3_client.delete_files(note.image_urls)
        await s3_client.delete_files(note.audio_urls)
    else:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заметка не найдена",
        )
    
    # Удаляем из БД
    await NotesRepo.delete_note(note_id)
    
    return {"msg": f"Заметка с ID {note_id} успешно удалена"}


@router.get("/get_all")
async def get_notes():
    notes = await NotesRepo.get_all_notes()
    
    return {"data": notes}
