from flask import Blueprint, jsonify

api = Blueprint('api', __name__)


@api.route('/')
def index():
    return jsonify(**{'result': 'success'})
