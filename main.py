import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from core.settings import settings
from api.v1_0.api import api_router as api_router__v1_0

app = FastAPI(
    title=settings.TITLE,
    openapi_url=settings.OPENAPI_URL,
    docs_url=settings.DOCS_URL,
    redoc_url=None,
    version='0.0.0'
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOW_METHODS,
    allow_headers=settings.ALLOW_HEADERS
)
app.include_router(api_router__v1_0, prefix=settings.API__v1_0)

if __name__ == '__main__':
    uvicorn.run('main:app', port=8080, host='0.0.0.0', reload=True)
