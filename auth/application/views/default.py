from flask import current_app, Blueprint, jsonify

default = Blueprint('default', __name__)

@default.route('/')
def index():
    current_app.logger.debug("From APP")
    return jsonify(**{'result': 'success'})


@default.route('/login', methods=['GET', 'POST'])
def login():
    return dict()
