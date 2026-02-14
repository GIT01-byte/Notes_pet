from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class NoteBase(BaseModel):
    user: str
    title: str
    content: str
    video_uuid: list[str]
    image_uuid: list[str]
    audio_uuid: list[str]


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    video_uuid: Optional[list[str]] = None
    image_uuid: Optional[list[str]] = None
    audio_uuid: Optional[list[str]] = None


class NoteRead(NoteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class NoteDelete(BaseModel):
    id: int
    username: str
