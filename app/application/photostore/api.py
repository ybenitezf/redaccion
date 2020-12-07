from flask import Blueprint

photostore_api = Blueprint(
    'photos_api', __name__, template_folder='templates')
