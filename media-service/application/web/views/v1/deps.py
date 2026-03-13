from fastapi import UploadFile

from application.core.files.schemas.files import UploadContext

# from application.repositories.database.db_helper import db_helper

# DbSessionDep = Annotated[
#     AsyncSession, Depends(db_helper.session_getter)
# ]  # TODO add dishka di


class FileUploadInputDTO:
    def __init__(
        self,
        file: UploadFile,
        upload_context: UploadContext,
        entity_id: int,
    ):
        self.file = file
        self.upload_context = upload_context
        self.entity_id = entity_id
