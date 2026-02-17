from sqlalchemy import String, Table, Column, Integer, MetaData, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models_crud import (
    media_uuid,
    media_s3_url,
    created_at,
    updated_at,
)
from .base import Base


class NotesOrm(Base):
    user: Mapped[str] = mapped_column(nullable=False)

    title: Mapped[str] = mapped_column(unique=True, nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    video_files: Mapped["VideoFilesOrm"] = relationship(
        back_populates="notes",
        lazy="selectin",
    )
    
    image_files: Mapped["ImageFilesOrm"] = relationship(
        back_populates="notes",
        lazy="selectin",
    )
    
    audio_files: Mapped["AudioFilesOrm"] = relationship(
        back_populates="notes",
        lazy="selectin",
    )


class VideoFilesOrm(Base):
    note_id: Mapped[int] = mapped_column(ForeignKey("notes.id"))

    uuid: Mapped[media_uuid]
    s3_url: Mapped[media_s3_url]
    note: Mapped["NotesOrm"] = relationship(
        back_populates="video_files",
        lazy="selectin",
    )


class ImageFilesOrm(Base):
    note_id: Mapped[int] = mapped_column(ForeignKey("notes.id"))

    uuid: Mapped[media_uuid]
    s3_url: Mapped[media_s3_url]
    note: Mapped["NotesOrm"] = relationship(
        back_populates="image_files",
        lazy="selectin",
    )


class AudioFilesOrm(Base):
    note_id: Mapped[int] = mapped_column(ForeignKey("notes.id"))

    uuid: Mapped[media_uuid]
    s3_url: Mapped[media_s3_url]
    note: Mapped["NotesOrm"] = relationship(
        back_populates="audio_files",
        lazy="selectin",
    )
