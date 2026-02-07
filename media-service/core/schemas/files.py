import datetime
from pydantic import BaseModel, ConfigDict


class FileMetadataBase(BaseModel):
    uuid: str
    
    s3_url: str
    filename: str
    size: int
    content_type: str
    
    uploaded_at_s3: datetime.datetime


class FileMeatadataCreate(FileMetadataBase):
    pass


class FileMeatadataRead(FileMetadataBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class FileMetadataDelete(BaseModel):
    id: int
