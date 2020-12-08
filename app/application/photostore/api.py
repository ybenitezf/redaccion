from flask import Blueprint, current_app, abort
from flask.globals import request

photostore_api = Blueprint(
    'photos_api', __name__, template_folder='templates')


