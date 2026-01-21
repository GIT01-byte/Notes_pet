from fastapi import Form
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str = Form()
    password: str = Form()
