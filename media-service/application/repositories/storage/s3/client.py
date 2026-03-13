import asyncio
from contextlib import asynccontextmanager
from typing import BinaryIO

from aiobotocore.session import get_session

from application.exceptions.exceptions import (
    S3DeleteObjectFailedError,
    S3PutObjectFailedError,
)
from application.utils.logging import logger


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

    async def put_object(self, file: BinaryIO, key: str):
        try:
            async with self.get_client() as client:
                await client.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=file,
                )  # type: ignore

            logger.info(f"[S3] Файл загружен: {key}")
        except Exception as e:
            logger.exception(f"[S3] Ошибка загрузки: {key}")
            raise S3PutObjectFailedError(
                detail=f"Failed to upload {key}: {str(e)}"
            ) from e

    async def head_object(self, key: str) -> bool:
        """Проверяет существование объекта в S3."""
        try:
            async with self.get_client() as client:
                await client.head_object(Bucket=self.bucket_name, Key=key)  # type: ignore
            return True
        except Exception:
            logger.warning(f"[S3] Файл не найден: {key}")
            return False

    async def delete_object(self, key: str):
        try:
            async with self.get_client() as client:
                await client.delete_object(Bucket=self.bucket_name, Key=key)  # type: ignore

            logger.info(f"[S3] Файл удален: {key}")
        except Exception as e:
            logger.exception(f"[S3] Ошибка удаления: {key}")
            raise S3DeleteObjectFailedError(
                detail=f"Failed to delete {key}: {str(e)}"
            ) from e

    async def move_file(
        self,
        src_key: str,
        dest_key: str,
    ):
        """Перемещает файл в S3, копируя и удаляя оригинал."""
        try:
            async with self.get_client() as client:
                copy_source = {"Bucket": self.bucket_name, "Key": src_key}
                await client.copy_object(
                    CopySource=copy_source,
                    Bucket=self.bucket_name,
                    Key=dest_key,
                )  # type: ignore
                await client.delete_object(
                    Bucket=self.bucket_name,
                    Key=src_key,
                )  # type: ignore
            logger.info(f"[S3] Файл перемещен: {src_key} -> {dest_key}")
        except Exception as e:
            logger.exception(f"[S3] Ошибка перемещения: {src_key} -> {dest_key}")
            # При неудаче удаляем файлы
            try:
                await client.delete_object(Bucket=self.bucket_name, Key=dest_key)  # type: ignore
            except Exception:
                pass
            raise S3DeleteObjectFailedError(
                detail=f"Failed to move {src_key} to {dest_key}: {str(e)}"
            ) from e

    async def get_file_url(self, key: str) -> str:
        """Генерирует публичный URL для файла в S3."""
        return f"{self.config['endpoint_url']}/{key}"

    async def convert_url_to_key(self, url: str) -> str:
        """Конвертирует S3 URL в ключ объекта."""
        if url.startswith(self.config["endpoint_url"]):
            return url.removeprefix(self.config["endpoint_url"] + "/")
        raise ValueError(f"URL не принадлежит этому S3 хранилищу: {url}")


if __name__ == "__main__":

    async def main():
        client = S3Client(
            access_key="755a7b2350b5443db2bccacc41dd5370",
            secret_key="f1a0eacf1a8c40b49a696a7a5895767f",
            endpoint_url="https://8e731fa2-5524-4d50-823b-1ee7780a3226.selstorage.ru",
            bucket_name="test-public-bucket-12414",
        )
        # Используй key напрямую, а не URL
        url = "https://8e731fa2-5524-4d50-823b-1ee7780a3226.selstorage.ru/UploadContext.avatar/15/avatar/8e1e4ba7-4c5b-4b12-bede-35cb72588218.jpg"
        key = await client.convert_url_to_key(url=url)
        response = await client.head_object(key=key)
        print(response)

        # Если нужен URL для браузера:
        file_url = await client.get_file_url(key=key)
        print(f"URL для браузера: {file_url}")

    asyncio.run(main())
