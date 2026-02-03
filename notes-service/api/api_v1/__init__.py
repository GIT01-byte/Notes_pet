from fastapi import APIRouter

from core.config import settings

from .notes import router as notes_router


router = APIRouter(
    prefix=settings.api.v1.prefix
)
router.include_router(
    notes_router,
)
