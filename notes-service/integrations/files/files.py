from fastapi import Request, HTTPException, status

import httpx

from .schemas import NotesServiceFileUploadRequest

from utils.logging import logger


async def upload_file(request: NotesServiceFileUploadRequest):
    async with httpx.AsyncClient() as client:
        try:
            files = {
                'file': (
                    request.file.filename,
                    request.file.file,
                    request.file.content_type
                )
            }
            logger.info(f"upload_file файл - {request.file.filename}")
            
            query_params = {
                "upload_context": request.upload_context,
                "entity_uuid": request.entity_uuid,
            }
            logger.info(f"upload_file запросил - {query_params}")
            
            upload_response = await client.post(
                    url=f"http://krakend:8080/media_service/upload",
                    params=query_params,
                    files=files,
                    follow_redirects=True,
                )
            
            if upload_response.status_code != 200:
                logger.exception(f"Upload file failed: {upload_response.text}") 
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Upload file failed: {upload_response.text}"
                )

            response_data = upload_response.json()
            logger.info(f"upload_file обработал - {response_data}")
            
            return {
                "ok": response_data["ok"],
                "message": response_data["message"],
                "uuid": response_data["uuid"]
            }
        except httpx.RequestError as exc:
            logger.exception(f"Gateway unavailable: {exc}") 
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Media service unavailable")
        except KeyError as exc:
            logger.exception(f"Invalid response format: {exc}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid response from media service")
        except Exception as exc:
            logger.exception(f"Unexpected error: {exc}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
        