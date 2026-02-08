from pathlib import Path

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_PATH = Path(__file__).parent.parent
ENV_PATH = BASE_PATH / ".env"


class AppConfig(BaseModel):
    mode: str = "DEV"
    host: str = "0.0.0.0"
    port: int = 8003


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    service: str = "/media_service"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class DatabaseSettings(BaseModel):
    # DB URL
    host: str
    port: int
    user: str
    pwd: str
    name: str
    # Other DB settings
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    @property
    def DB_URL_asyncpg(self):
        return f"postgresql+asyncpg://{self.user}:{self.pwd}@{self.host}:{self.port}/{self.name}"


class S3Settings(BaseModel):
    accesskey: str
    secretkey: str
    endpointurl: str
    bucketname: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        case_sensitive=False,
        env_nested_delimiter="_",
        env_prefix="MEDIA-SERV_",
    )
    app: AppConfig = AppConfig()
    api: ApiPrefix = ApiPrefix()
    db: DatabaseSettings
    s3: S3Settings


settings = Settings()  # type: ignore
print()
print("-------- Media Service --------")
print(f"INFO:     Run mode: {settings.app.mode}")
print(f"INFO:     Using S3 url: {settings.s3.endpointurl}/{settings.s3.bucketname}")
print("------------------------------")
print()
