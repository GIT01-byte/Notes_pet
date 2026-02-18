from typing import List

from fastapi import Query, UploadFile


class NoteCreateForm:
    def __init__(
        self,
        title: str = Query(str),
        content: str = Query(str),
    ):
        self.title = title
        self.content = content


class NoteCreateMediaFilesForm:
    def __init__(
        self,
        video_files: List[UploadFile] | None = None,
        image_files: List[UploadFile] | None = None,
        audio_files: List[UploadFile] | None = None,
    ):
        self.video_files = video_files
        self.image_files = image_files
        self.audio_files = audio_files
