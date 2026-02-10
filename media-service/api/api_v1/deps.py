from fastapi import UploadFile

class FileUploadRequest:
    def __init__(
        self,
        file: UploadFile,
        upload_type: str,
        entity_id: str,
    ):
        self.file = file
        self.upload_type = upload_type
        self.entity_id = entity_id
    