import datetime
import uuid

from pydantic import BaseModel, ConfigDict


class FileMetadataBase(BaseModel):
    uuid: uuid.UUID

    s3_url: str
    filename: str
    size: int
    content_type: str


class FileMeatadataCreate(FileMetadataBase):
    pass


class FileMeatadataRead(FileMetadataBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class FileMetadataDelete(BaseModel):
    id: int
