from fastapi import UploadFile

class FileUploadRequest:
    def __init__(
        self,
        user_id: int,
        file: UploadFile,
        filename: str,
    ):
        self.user_id = user_id
        self.file = file
        self.filename = filename
    