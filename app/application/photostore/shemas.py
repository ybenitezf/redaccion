from flask.globals import request
from application.photostore.models import PhotoCoverage
from application import ma
from marshmallow import fields

class PhotoCoverageSchema(ma.SQLAlchemySchema):
    class Meta:
        model = PhotoCoverage
    id = ma.auto_field()
    headline = ma.auto_field()
    excerpt = ma.auto_field()
    credit_line = ma.auto_field()
    keywords = fields.List(fields.Str())
    photos = fields.List(fields.Str())
