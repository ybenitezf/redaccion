from application import db
from application.models import _gen_uuid


class User(db.Model):
    id = db.Column(db.String(32), primary_key=True, default=_gen_uuid)
    name = db.Column(db.String(120))
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
