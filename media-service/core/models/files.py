from sqlalchemy.orm import mapped_column, Mapped

from core.crud.db_crud import (
    created_at,
    updated_at,
)

from .base import Base


class FileMetadataOrm(Base):
    S3_url: Mapped[str] = mapped_column(unique=True, nullable=False)
    
    file_name: Mapped[str] = mapped_column(unique=True, nullable=False)
    file_size: Mapped[int] = mapped_column(nullable=False)
    file_type: Mapped[str] = mapped_column(nullable=False)
    
    uploaded_at: Mapped[created_at]
    