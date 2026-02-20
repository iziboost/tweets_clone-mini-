from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.media import Media
from app.models.user import User
from app.schemas.error import ErrorResponse

router = APIRouter(tags=["medias"])

MEDIA_ROOT = Path("media")

@router.post(
    "/medias",
    responses={
        200: {"description": "Media uploaded"},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
    },
)
async def upload_media(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only images are allowed")

    MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}_{file.filename}"
    path = MEDIA_ROOT / filename

    with path.open("wb") as buffer:
        content = await file.read()
        buffer.write(content)

    media = Media(file_path=str(path))
    db.add(media)
    await db.commit()
    await db.refresh(media)

    return {"result": True, "media_id": media.id}