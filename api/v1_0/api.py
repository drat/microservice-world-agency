from fastapi import APIRouter

from .endpoints import facebook

api_router = APIRouter()
api_router.include_router(
    facebook.api_router,
    prefix=facebook.prefix,
    tags=facebook.tags
)
