from fastapi import APIRouter

from core.config import settings
from core.schemas import NoteRead, NoteCreate, NoteSchema

from core.notes_repo import NotesRepo

router = APIRouter(
    prefix=settings.api.v1.notes,
    tags=["Notes"]
)


@router.get("/get_all", response_model=list[NoteRead])
async def get_notes():
    notes = await NotesRepo.get_all_notes()
    return notes


@router.post("/create", response_model=NoteRead)
async def create_notes(
    note_create: NoteCreate,
):
    note = await NotesRepo.create_note(note_to_create=note_create)
    return note
