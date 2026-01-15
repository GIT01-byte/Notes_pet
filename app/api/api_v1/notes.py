import shutil
from typing import Optional
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from core.s3_client import s3_client
from core.config import settings
from core.notes_repo import NotesRepo
from core.schemas.notes import NoteRead

from core.s3_client import s3_client
from .deps import NoteCreateForm

router = APIRouter(
    prefix=settings.api.v1.notes,
    tags=["Notes"]
)


UPLOAD_DIR = Path("uploaded_files")

FILE_MAP = {
    "videos": ["mp4", "avi", "webm"],
    "photos": ["jpeg", "jpg", "png", "webp"],
    "audios": ["mp3", "ogg", "wav"],
}

# Инициализация папок при запуске
for folder in FILE_MAP.keys():
    (UPLOAD_DIR / folder).mkdir(parents=True, exist_ok=True)


def get_file_category(filename: str):
    extension = filename.split(".")[-1].lower()
    print(extension)
    for category, excentions in FILE_MAP.items():
        if not extension in excentions:
            continue
        return category
    else:
        return "others"


@router.post("/upload-file")
async def upload_file(uploaded_file: UploadFile):
    if not uploaded_file.filename:
        raise HTTPException(status_code=400, detail="Имя файла отсутствует")

    category = get_file_category(uploaded_file.filename)
    if category == "others":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неподдерживаемый формат файла"
        )

    # Защита от Path Traversal: создаем безопасное имя
    file_extension = Path(uploaded_file.filename).suffix
    safe_name = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / category / safe_name # type: ignore

    # Сохраняем файл эффективно (стримом, а не целиком в память)
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)

    return {
        "message": "Успешно загружено", 
        "filename": safe_name,
        "category": category
    }

# Объединенный эндпоинт для получения файлов
@router.get("/files/{category}/{filename}")
async def get_file(category: str, filename: str):
    if category not in FILE_MAP:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    
    # Безопасное извлечение имени файла
    safe_filename = Path(filename).name 
    file_path = UPLOAD_DIR / category / safe_filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Файл не найден")

    return FileResponse(path=file_path)


@router.get("/get_all", response_model=list[NoteRead])
async def get_notes():
    notes = await NotesRepo.get_all_notes()
    return notes


@router.post("/create")
async def create_notes(
    note_create_form: NoteCreateForm = Depends(),
):
    # Медиа-файлы отправляем в S3 и формируем ссылки
    if note_create_form.video_files:
        for file in note_create_form.video_files:
            print(f"Обнаружен видео-файл: {file.filename}")
            await s3_client.upload_file(file=file.file, filename=file.filename) # type: ignore
            file_url = await s3_client.get_file_url(filename=file.filename)  # type: ignore
            if file_url:
                print(f"Ссылка на файл ({file.filename!r}): {file_url}")
            
    if note_create_form.photo_files:
        for file in note_create_form.photo_files:
            print(f"Обнаружен фото-файл: {file.filename}")
            await s3_client.upload_file(file=file.file, filename=file.filename) # type: ignore
            file_url = await s3_client.get_file_url(filename=file.filename)  # type: ignore
            if file_url:
                print(f"Ссылка на файл ({file.filename=!r}): {file_url}")
            
    if note_create_form.audio_files:
        for file in note_create_form.audio_files:
            await s3_client.upload_file(file=file.file, filename=file.filename) # type: ignore
            file_url = await s3_client.get_file_url(filename=file.filename)  # type: ignore
            if file_url:
                print(f"Ссылка на файл ({file.filename=!r}): {file_url}")
    
    # 

    # Отправляем в БД
    # note = await NotesRepo.create_note(...)
    return note_create_form.title
