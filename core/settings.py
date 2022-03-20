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

    API_DATABASE_NAME: str = 'world-agency'
    API_DATABASE_HOST: str = '103.141.141.121'
    API_DATABASE_PORT = 5432
    API_DATABASE_USERNAME = 'postgres'
    API_DATABASE_PASSWORD = '^Tuan27121998'


settings = Settings()
