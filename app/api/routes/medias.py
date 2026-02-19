from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.models.user import User
from app.models.media import Media
from app.schemas.media import CreateMediaResponse
from app.schemas.error import ErrorResponse
from app.api.deps import get_current_user
from app.core.database import get_db

router = APIRouter(tags=["medias"])

MEDIA_ROOT = Path("media")

@router.post(
    "/medias",
    response_model=CreateMediaResponse,
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
) -> CreateMediaResponse:
    if not file.content_type.startswith("image/"):
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

    return CreateMediaResponse(result=True, media_id=media.id)