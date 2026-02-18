from typing import List
from uuid import UUID, uuid7

from sqlalchemy import String, Table, Column, Integer, MetaData, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models_crud import (
    created_at,
    updated_at,
)
from .base import Base


class FileBase:
    uuid: Mapped[UUID] = mapped_column(unique=True, default=uuid7, index=True)
    s3_url: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)

    uploaded_at_s3: Mapped[str]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class NotesOrm(Base):
    user: Mapped[str] = mapped_column(nullable=False)

    title: Mapped[str] = mapped_column(unique=True, nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    video_files: Mapped[List["VideoFilesOrm"]] = relationship(
        back_populates="note",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    image_files: Mapped[List["ImageFilesOrm"]] = relationship(
        back_populates="note",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    audio_files: Mapped[List["AudioFilesOrm"]] = relationship(
        back_populates="note",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, "video_files") or self.video_files is None:
            self.video_files = []
        if not hasattr(self, "image_files") or self.image_files is None:
            self.image_files = []
        if not hasattr(self, "audio_files") or self.audio_files is None:
            self.audio_files = []


class VideoFilesOrm(Base, FileBase):
    note_id: Mapped[int] = mapped_column(
        ForeignKey("notes_orms.id", ondelete="CASCADE")
    )

    note: Mapped["NotesOrm"] = relationship(
        back_populates="video_files",
    )


class ImageFilesOrm(Base, FileBase):
    note_id: Mapped[int] = mapped_column(
        ForeignKey("notes_orms.id", ondelete="CASCADE")
    )

    note: Mapped["NotesOrm"] = relationship(
        back_populates="image_files",
    )


class AudioFilesOrm(Base, FileBase):
    note_id: Mapped[int] = mapped_column(
        ForeignKey("notes_orms.id", ondelete="CASCADE")
    )

    note: Mapped["NotesOrm"] = relationship(
        back_populates="audio_files",
    )
