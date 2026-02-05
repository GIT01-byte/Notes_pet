from fastapi import UploadFile

from core.s3.s3_client import s3_client


class MediaService:
    async def upload_file(self, file: UploadFile, filename: str):
        await s3_client.upload_file(file=file.file, filename=filename)