import asyncio
from contextlib import asynccontextmanager
from typing import BinaryIO

from aiobotocore.session import get_session

from .config import settings


class S3Client:
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        endpoint_url: str,
        bucket_name: str,
    ):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
        }
        self.bucket_name = bucket_name
        self.session = get_session()
    
    @asynccontextmanager    
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client
    
    async def upload_file(
        self,
        file: BinaryIO,
        filename: str
    ):
        async with self.get_client() as client:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=file,
            ) # type: ignore
            print(f"Файл: {filename} добавлен в S3")
    
    async def get_file_url(
        self,
        filename: str,
    ):
        async with self.get_client() as client:
            try:
            # Генерируем ссылку для скачивания
                url = f"{self.config["endpoint_url"]}/{filename}"
                return url
            except Exception as e:
                print(f"Ошибка при генерации ссылки: {e}")
                return None
    

s3_client = S3Client(
    access_key=settings.s3.access_key,
    secret_key=settings.s3.secret_access_key,
    endpoint_url=settings.s3.endpoint_url,
    bucket_name=settings.s3.bucket_name,
)


if __name__ == "__main__":
    async def main():
        file_url = await s3_client.get_file_url(filename='video.mp4')
        if file_url:
            print(f"Временная ссылка для скачивания: {file_url}")
    
    asyncio.run(main())
