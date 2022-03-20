import peewee

from core.database import db


class Base(peewee.Model):
    id = peewee.UUIDField(
        index=True,
        unique=True,
        primary_key=True
    )

    class Meta:
        database = db
