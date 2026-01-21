from typing import List

from fastapi import Request, UploadFile, HTTPException, status

import httpx

from notes.core.schemas.users import RequestUserData

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


class NoteCreateForm:
    def __init__(
        self,
        title: str,
        content: str,
        video_files: List[UploadFile] | None = None,
        image_files: List[UploadFile] | None = None,
        audio_files: List[UploadFile] | None = None,
    ):
        self.title = title
        self.content = content
        self.video_files = video_files
        self.image_files = image_files
        self.audio_files = audio_files


async def get_current_user(request: Request):
    async with httpx.AsyncClient() as client:
        try:
            access_token = request.cookies.get(ACCESS_TOKEN_TYPE)
            refresh_token = request.cookies.get(REFRESH_TOKEN_TYPE)
            
            if access_token and refresh_token:
                tokens_cookies = {
                    ACCESS_TOKEN_TYPE: access_token,
                    REFRESH_TOKEN_TYPE: refresh_token,
                }
                
                login_response = await client.get(
                    "http://krakend:8080/users/me/", 
                    cookies=tokens_cookies,
                    follow_redirects=True,
                )
            else:
                raise HTTPException(status_code=500, detail=f"Get cookie fail")
            
            if login_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail=f"Authorization failed: {login_response.text}"
                )

            response_data = login_response.json()
            
            return RequestUserData(
                user_id=response_data["user_id"],
                username=response_data["username"],
                email=response_data["email"],
                is_active=response_data["is_active"],
                jti=response_data["jti"],
                iat=response_data["iat"],
            )
            
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Gateway unavailable: {exc}")
        