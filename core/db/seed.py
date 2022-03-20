from core.database import db
from core.db.models.facebook import Facebook


def initial():
    db.connect()
    db.create_tables([Facebook])
    db.close()
