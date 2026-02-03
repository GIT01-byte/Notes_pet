from sqlalchemy import MetaData
from sqlalchemy.orm import (
    DeclarativeBase, 
    Mapped, 
    mapped_column,
    declared_attr,
)

from utils import camel_case_to_snake_case

from core.models_crud import intpk
from core.config import settings


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention=settings.db.naming_convention,
    )
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{camel_case_to_snake_case(cls.__name__)}s"
    
    id: Mapped[intpk]
