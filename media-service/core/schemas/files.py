import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from utils.constants import NOTES_ATTACHMENT_NAME, USERS_AVATAR_NAME


class UploadContext(str, Enum):
    post_attachment = NOTES_ATTACHMENT_NAME
    avatar = USERS_AVATAR_NAME
    # document = DOCUMENT_NAME


class FileMetadataBase(BaseModel):
    uuid: UUID

    s3_url: str
    filename: str
    size: int
    content_type: str
    category: str
    status: str


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
