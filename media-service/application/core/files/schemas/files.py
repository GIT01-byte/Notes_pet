import datetime
from enum import Enum
from uuid import UUID

from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict

from application.utils.constants import NOTES_ATTACHMENT_NAME, USERS_AVATAR_NAME


class FileProcessUCInputDTO(BaseModel):
    file: UploadFile
    upload_context: str
    entity_id: int


class FileProcessUCOuputDTO(BaseModel):
    validaion_status: bool

    file_id: UUID

    unique_filename: str
    category: str

    s3_temp_upload_key: str
    s3_upload_key: str


class FileUploadUCInputDTO(BaseModel):
    file: UploadFile

    file_id: UUID

    upload_context: str
    entity_id: int

    unique_filename: str
    size: int
    content_type: str
    category: str

    s3_temp_upload_key: str
    s3_upload_key: str


class FileUploadUCOutputDTO(BaseModel):
    upload_status: str

    file_id: UUID

    size: int
    unique_filename: str
    content_type: str
    category: str


class UploadContext(str, Enum):
    post_attachment = NOTES_ATTACHMENT_NAME
    avatar = USERS_AVATAR_NAME
    # document = DOCUMENT_NAME


class FileMetadataBase(BaseModel):
    file_id: UUID

    entity_id: int
    upload_context: UploadContext
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
