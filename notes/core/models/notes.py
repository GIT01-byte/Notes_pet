from sqlalchemy.orm import mapped_column, Mapped

from core.models_crud import (
    media_url,
    created_at,
    updated_at,
)
from .base import Base


class NotesOrm(Base):
    user: Mapped[str] = mapped_column(nullable=False)
    
    title: Mapped[str] = mapped_column(unique=True, nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    
    video_urls: Mapped[media_url]
    image_urls: Mapped[media_url]
    audio_urls: Mapped[media_url]
    
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    