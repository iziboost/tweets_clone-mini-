
from fastapi import APIRouter

from app.api.routes import tweets, users, likes, follows, medias

api_router = APIRouter(prefix="/api")
api_router.include_router(tweets.router)
api_router.include_router(users.router)
api_router.include_router(likes.router)
api_router.include_router(follows.router)
api_router.include_router(medias.router)