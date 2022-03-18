from fastapi import APIRouter

from .endpoints import facebook

apiRouter = APIRouter()
apiRouter.include_router(
    facebook.apiRouter,
    prefix=facebook.prefix,
    tags=facebook.tags
)
