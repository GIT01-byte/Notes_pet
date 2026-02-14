from fastapi import UploadFile

from core.schemas.files import UploadContext


class FileUploadRequest:
    def __init__(
        self,
        file: UploadFile,
        upload_context: UploadContext,
        entity_id: str,
    ):
        self.file = file
        self.upload_context = upload_context
        self.entity_id = entity_id
    