from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class NoteBase(BaseModel):
    title: str
    content: str
    video_urls: list[str]
    image_urls: list[str]
    audio_urls: list[str]


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    video_urls: Optional[list[str]] = None
    image_urls: Optional[list[str]] = None
    audio_urls: Optional[list[str]] = None


class NoteRead(NoteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class NoteDelete(BaseModel):
    id: int
