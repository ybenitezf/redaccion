from application.models.content import Article
from flask import Blueprint, jsonify, render_template
from flask_login import login_required


default = Blueprint('default', __name__)


@default.route('/')
@login_required
def index():
    return render_template('default/index.html')


@default.route('/escribir')
def write():
    return render_template('default/write.html')
