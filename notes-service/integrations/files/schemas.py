from fastapi import UploadFile
from pydantic import BaseModel

    
class NotesServiceFileUploadRequest(BaseModel):
    upload_context: str
    file: UploadFile
    entity_uuid: str
