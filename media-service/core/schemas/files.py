from pydantic import BaseModel, ConfigDict


class FileBase(BaseModel):
    filename: str


class FileCreate(FileBase):
    pass


class FileRead(FileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class FileDelete(BaseModel):
    id: int
