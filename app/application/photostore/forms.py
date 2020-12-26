from flask_wtf import FlaskForm
from wtforms import StringField


class SearchPhotosForm(FlaskForm):
    userquery = StringField('userquery')
