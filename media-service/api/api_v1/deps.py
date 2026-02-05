from fastapi import UploadFile

class FileUploadRequest:
    def __init__(
        self,
        file: UploadFile,
        filename: str,
    ):
        self.file = file
        self.filename = filename
    