from sqlalchemy.orm import mapped_column, Mapped

from core.models_crud import (
    media_url,
    created_at,
    updated_at,
)
from .base import Base


class NotesOrm(Base):
    title: Mapped[str] = mapped_column(unique=True, nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    
    video_link = Mapped[media_url]
    photo_link = Mapped[media_url]
    audio_link = Mapped[media_url]
    
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    
    # user: Mapped["UsersOrm"] = relationship(
    #     back_populates="notes",
    # )
