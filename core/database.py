import peewee
from playhouse.postgres_ext import PostgresqlExtDatabase
from contextvars import ContextVar

from core.settings import settings

db_state_default = {
    'closed': None,
    'conn': None,
    'ctx': None,
    'transactions': None
}
db_state = ContextVar('db_state', default=db_state_default.copy())


class PeeweeConnectionState(peewee._ConnectionState):
    def __init__(self, **kwargs):
        super().__setattr__('_state', db_state)
        super().__init__(**kwargs)

    def __setattr__(self, name: str, value) -> None:
        self._state.get()[name] = value

    def __getattr__(self, name: str):
        return self._state.get()[name]


db = PostgresqlExtDatabase(
    database=settings.API_DATABASE_NAME,
    host=settings.API_DATABASE_HOST,
    port=settings.API_DATABASE_PORT,
    user=settings.API_DATABASE_USERNAME,
    password=settings.API_DATABASE_PASSWORD,
    max_connections=None
)

db._state = PeeweeConnectionState()
