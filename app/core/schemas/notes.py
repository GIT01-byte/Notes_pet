from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class NoteBase(BaseModel):
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

    video_urls: List[str] = []
    photo_urls: List[str] = []
    audio_urls: List[str] = []


class NoteDelete(BaseModel):
    id: int
