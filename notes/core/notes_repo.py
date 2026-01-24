from typing import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper, NotesOrm
from core.schemas import NoteCreate, NoteDelete, NoteUpdate


class NotesRepo:
    @staticmethod
    async def get_all_notes() -> Sequence[NotesOrm]:
        async with db_helper.session_factory() as session:
            stmt = select(NotesOrm).order_by(NotesOrm.id)
            result = await session.scalars(stmt)
            return result.all()
    
    
    @staticmethod
    async def get_user_notes(username: str):
        async with db_helper.session_factory() as session:
            stmt = select(NotesOrm).where(NotesOrm.user == username)
            result = await session.scalars(stmt)
            return result.all()


    @staticmethod
    async def get_note(note_id: int):
        async with db_helper.session_factory() as session:
            stmt = select(NotesOrm).where(NotesOrm.id == note_id)
            result = await session.scalars(stmt)
            return result.first()
    

    @staticmethod
    async def create_note(note_to_create: NoteCreate):
        async with db_helper.session_factory() as session:
            new_note = NotesOrm(**note_to_create.model_dump())
            session.add(new_note)
            await session.commit()
            await session.refresh(new_note)
            return new_note
        
    
    @staticmethod
    async def delete_note(note_id: int):
        async with db_helper.session_factory() as session:
            stmt = delete(NotesOrm).where(NotesOrm.id == note_id)
            await session.execute(stmt)
            await session.commit()
    