import asyncio
from contextlib import asynccontextmanager
from typing import BinaryIO
from urllib.parse import urlparse

from aiobotocore.session import get_session

from core.config import settings


def decode_s3_file_url(file_url: str):
    filename = urlparse(file_url).path
    return filename


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
        try:
            # Генерируем ссылку для скачивания
            url = f"{self.config["endpoint_url"]}/{filename}"
            return url
        except Exception as e:
            print(f"Ошибка при генерации ссылки: {e}")
            return None
    
    async def delete_files(
        self,
        file_urls: list[str],
    ):
        try:
            async with self.get_client() as client:
                for url in file_urls:
                    filename = decode_s3_file_url(url)
                    response = await client.delete_object(
                        Bucket=self.bucket_name,
                        Key=filename
                    ) # type: ignore
                    print(f"Файл {filename} удален из {self.bucket_name}. Ответ: {response}")
        except Exception as e:
            print(f"Ошибка при удалении {file_urls}: {e}")
    

s3_client = S3Client(
    access_key=settings.s3.accesskey,
    secret_key=settings.s3.secretkey,
    endpoint_url=settings.s3.endpointurl,
    bucket_name=settings.s3.bucketname,
)
