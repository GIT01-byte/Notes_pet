import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class FileMetadataBase(BaseModel):
    uuid: UUID

    s3_url: str
    filename: str
    size: int
    content_type: str


class FileMeatadataCreate(FileMetadataBase):
    pass


class FileMeatadataRead(FileMetadataBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at_db: datetime.datetime
    updated_at_db: datetime.datetime


class FileMetadataDelete(BaseModel):
    id: int


class FileValidation(BaseModel):
    validaion_status: bool
    category: str
    filename: str
    
