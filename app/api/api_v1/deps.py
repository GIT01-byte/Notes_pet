from typing import List, Optional

from fastapi import File, Form, UploadFile


class NoteCreateForm:
    def __init__(
        self,
        title: str,
        content: str,
        video_files: List[UploadFile] | None = None,
        photo_files: List[UploadFile] | None = None,
        audio_files: List[UploadFile] | None = None,
    ):
        self.title = title
        self.content = content
        self.video_files = video_files
        self.photo_files = photo_files
        self.audio_files = audio_files
