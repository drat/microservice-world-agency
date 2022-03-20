import peewee
from playhouse import postgres_ext

from core.db.models.base import Base


class Facebook(Base):
    uid = peewee.TextField(
        index=True,
        unique=True
    )
    cookie = peewee.TextField()
    graph = postgres_ext.BinaryJSONField(
        null=True
    )
    created_time = peewee.TimestampField()
    updated_time = peewee.TimestampField()
