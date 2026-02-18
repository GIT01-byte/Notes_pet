from typing import Optional
from pydantic import BaseModel, ConfigDict


class NoteBase(BaseModel):
    user: str
    title: str
    content: str


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class NoteRead(NoteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class NoteDelete(BaseModel):
    id: int
    username: str
