from sqlalchemy.orm import mapped_column, Mapped

from core.models_crud import (
    intpk,
    created_at,
    updated_at,
)
from .base import Base


class NotesOrm(Base):
    title: Mapped[str] = mapped_column(unique=True, nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    
    # user: Mapped["UsersOrm"] = relationship(
    #     back_populates="notes",
    # )
