from typing import List
from pydantic import BaseSettings


class Settings(BaseSettings):
    API__V1_0: str = '/api/v1.0'

    TITLE: str = 'Microservice World Agency'
    OPENAPI_URL: str = '/api/openapi.json'
    DOCS_URL: str = '/api/docs'

    ALLOW_ORIGINS: List[str] = ['*']
    ALLOW_METHODS: List[str] = ['*']
    ALLOW_HEADERS: List[str] = ['*']


settings = Settings()
