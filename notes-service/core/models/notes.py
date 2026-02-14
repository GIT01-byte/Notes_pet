from sqlalchemy.orm import mapped_column, Mapped

from core.models_crud import (
    media_uuid,
    created_at,
    updated_at,
)
from .base import Base


class NotesOrm(Base):
    user: Mapped[str] = mapped_column(nullable=False)
    
    title: Mapped[str] = mapped_column(unique=True, nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    
    video_uuid: Mapped[media_uuid]
    image_uuid: Mapped[media_uuid]
    audio_uuid: Mapped[media_uuid]
    
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    