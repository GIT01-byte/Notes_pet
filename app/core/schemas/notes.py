from pydantic import (
    BaseModel,
    ConfigDict,
)


class NoteSchema(BaseModel):
    title: str
    content: str


class NoteCreate(NoteSchema):
    pass


class NoteUpdate():
    new_title: str
    new_content: int


class NoteDelete():
    id: int


class NoteRead(NoteSchema):
    model_config = ConfigDict(
        from_attributes=True,
    )
    
    id: int
