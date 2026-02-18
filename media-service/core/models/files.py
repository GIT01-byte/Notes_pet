from uuid import UUID, uuid7 

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import mapped_column, Mapped

from core.crud.db_crud import (
    created_at,
    updated_at,
)

from .base import Base


class FilesMetadataOrm(Base):
    uuid: Mapped[UUID] = mapped_column(
        unique=True, 
        default=uuid7, 
        index=True
    )
    
    s3_url: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    
    status: Mapped[str] = mapped_column(String(20), default="pending")

    created_at_db: Mapped[created_at]
    updated_at_db: Mapped[updated_at]
    