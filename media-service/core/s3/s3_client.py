from contextlib import asynccontextmanager
from typing import BinaryIO
from urllib.parse import urlparse

from aiobotocore.session import get_session

from core.config import settings

from exceptions.exceptions import S3DeleteFileError, S3UploadFileError
from utils.logging import logger


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

    async def upload_file(self, file: BinaryIO, key: str):
        async with self.get_client() as client:
            try:
                logger.info(f"Загрузка файла: {key} в S3")
                await client.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=file,
                )  # type: ignore

                logger.info(f"Файл: {key} добавлен в S3")
                return {
                    "ok": True,
                    "message": f"Файл {key} успешно загружен в S3",
                }
            except Exception as e:
                logger.exception(f"Ошибка при добавлении файла в S3 {key}: {e}")
                raise S3UploadFileError

    async def get_file_url(self, key: str):
        try:
            # Генерируем ссылку для скачивания
            url = f"{self.config["endpoint_url"]}/{key}"
            return url
        except Exception as e:
            logger.exception(f"Ошибка при генерации ссылки: {e}")
            return None

    async def delete_file(self, key: str):
        try:
            async with self.get_client() as client:
                logger.info(f"Удаление файла {key} из {self.bucket_name}")
                response = await client.delete_object(
                    Bucket=self.bucket_name, Key=key
                )  # type: ignore

                logger.info(
                    f"Файл {key} удален из {self.bucket_name}. Ответ: {response}"
                )
                return {
                    "ok": True,
                    "message": f"Файл {key} успешно удален из S3",
                }
        except Exception as e:
            logger.exception(f"Ошибка при удалении {key}: {e}")
            raise S3DeleteFileError


s3_client = S3Client(
    access_key=settings.s3.accesskey,
    secret_key=settings.s3.secretkey,
    endpoint_url=settings.s3.endpointurl,
    bucket_name=settings.s3.bucketname,
)
