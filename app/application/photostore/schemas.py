from application.photostore.models import PhotoCoverage
from application.modules.editorjs import renderBlock
from application import ma
from marshmallow import fields, post_dump
from flask import json, current_app
from flask import render_template
from datetime import datetime

class PhotoCoverageSchema(ma.SQLAlchemySchema):
    class Meta:
        model = PhotoCoverage
    id = ma.auto_field()
    headline = ma.auto_field()
    excerpt = ma.auto_field()
    credit_line = ma.auto_field()
    keywords = fields.List(fields.Str())
    photos = fields.List(fields.Str())


class PhotoIndexSchema(ma.Schema):
    """Schema de la foto para indexar con Whoosh"""

    md5 = fields.Str()
    archive_on = fields.DateTime(format="%Y%m%d%H%M%S")
    taken_on = fields.DateTime(format="%Y%m%d%H%M%S")
    taken_by = fields.Str()
    archived = fields.Boolean()
    keywords = fields.List(fields.Str())
    credit_line = fields.Str()
    excerpt = fields.Str()
    headline = fields.Str()

    @post_dump
    def process_excerpt(self, data, many, **kwargs):
        field_data = json.loads(data.get('excerpt'))
        data['excerpt'] = render_template(
            'photostore/editorjs/photo_excerpt.txt', 
            data=field_data, 
            block_rederer=renderBlock)
        return data
