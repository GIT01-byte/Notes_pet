from typing import Optional
from uuid import UUID, uuid7

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

    video_files: Mapped[Optional["VideoFilesOrm"]] = relationship(
        back_populates="notes",
        order_by="VideoFilesOrm.id.desc()",
        lazy="joined",
    )

    image_files: Mapped[Optional["ImageFilesOrm"]] = relationship(
        back_populates="notes",
        order_by="ImageFilesOrm.id.desc()",
        lazy="joined",
    )

    audio_files: Mapped[Optional["AudioFilesOrm"]] = relationship(
        back_populates="notes",
        order_by="AudioFilesOrm.id.desc()",
        lazy="joined",
    )


class VideoFilesOrm(Base):
    note_id: Mapped[int] = mapped_column(ForeignKey("notes.id"))

    uuid: Mapped[UUID] = mapped_column(unique=True, default=uuid7, index=True)
    s3_url: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    notes: Mapped["NotesOrm"] = relationship(
        back_populates="video_files",
        lazy="selectin",
    )


class ImageFilesOrm(Base):
    note_id: Mapped[int] = mapped_column(ForeignKey("notes.id"))

    uuid: Mapped[UUID] = mapped_column(unique=True, default=uuid7, index=True)
    s3_url: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    notes: Mapped["NotesOrm"] = relationship(
        back_populates="image_files",
        lazy="selectin",
    )


class AudioFilesOrm(Base):
    note_id: Mapped[int] = mapped_column(ForeignKey("notes.id"))

    uuid: Mapped[UUID] = mapped_column(unique=True, default=uuid7, index=True)
    s3_url: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    notes: Mapped["NotesOrm"] = relationship(
        back_populates="audio_files",
        lazy="selectin",
    )
