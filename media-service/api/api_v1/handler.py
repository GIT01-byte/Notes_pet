from fastapi import APIRouter

from core.config import settings

from utils.logging import logger

router = APIRouter(prefix=settings.api.v1.handler, tags=["File Handler"])


@router.get("/health_check")
async def health_check():
    return {"success": "S3 File Handler started"}
