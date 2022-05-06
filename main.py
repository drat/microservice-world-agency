import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from core.settings import settings
from api.v1_0.api import apiRouter
from core.db import seed

seed.initial()
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
app.include_router(apiRouter, prefix=settings.API__V1_0)

if __name__ == '__main__':
    try:
        uvicorn.run('main:app', port=80, host='0.0.0.0', reload=True)
    except:
        uvicorn.run('main:app', port=8080, host='0.0.0.0', reload=True)

# import json
# from peewee import chunked

# from core.database import db
# from core.db.models.facebook import Facebook
# from uuid import UUID

# db.connect()
# db.create_tables([Facebook])

# fOpen = open('./backups/facebook_202204280543.json')
# database = json.load(fOpen)
# for batch in chunked(database['facebook'], 100000):
#     batch_map = []
#     for e in batch:
#         e['id'] = UUID(e['id'])
#         if e['graph'] is not None:
#             e['graph'] = json.loads(e['graph'])
#         batch_map.append(e)
#     Facebook.insert_many(batch_map).execute()
# fOpen.close()

# db.close()
