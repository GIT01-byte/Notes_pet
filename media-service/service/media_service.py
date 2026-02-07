from fastapi import UploadFile

from core.s3.s3_client import s3_client


class MediaService:
    async def upload_file(self, file: UploadFile, filename: str):
        try:
            await s3_client.upload_file(file=file.file, filename=filename)
        except:
            raise Exception("Error while uploading file")
        
    async def get_s3_url(self, filename: str):
        try:
            return await s3_client.get_file_url(filename=filename)
        except:
            raise Exception("Erroe while get file url")
        
    async def get_metadata_s3(self, filename: str):
        try:
            return await s3_client.get_file_metadata(filename=filename)
        except:
            raise Exception("Error while get file metadata")