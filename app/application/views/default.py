from flask import Blueprint, jsonify
from flask_login import login_required


default = Blueprint('default', __name__)


@default.route('/')
@login_required
def index():
    return jsonify(**{'result': 'success'})
