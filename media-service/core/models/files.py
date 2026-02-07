import datetime
from sqlalchemy.orm import mapped_column, Mapped

from core.crud.db_crud import (
    created_at,
    updated_at,
)

from .base import Base


class FilesMeatadataOrm(Base):
    uuid: Mapped[str] = mapped_column(primary_key=True, unique=True, nullable=False)
    s3_url: Mapped[str] = mapped_column(unique=True, nullable=False)
    
    filename: Mapped[str] = mapped_column(unique=True, nullable=False)
    size: Mapped[int] = mapped_column(nullable=False)
    content_type: Mapped[str] = mapped_column(nullable=False)

    created_at_db: Mapped[created_at]
    updated_at_db: Mapped[updated_at]
    