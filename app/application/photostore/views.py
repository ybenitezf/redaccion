from .models import PhotoCoverage
from flask_login import login_required
from flask import Blueprint, current_app, render_template, abort
from flask import request

photostore = Blueprint(
    'photos', __name__, template_folder='templates')


@photostore.route('/')
@login_required
def index():
    current_app.logger.debug(PhotoCoverage.query.all())
    return render_template('photostore/index.html')


@photostore.route('/upload-form')
@login_required
def upload_coverture():
    return render_template('photostore/upload.html')


@photostore.route('/upload', methods=['POST'])
def handle_upload():
    if 'image' not in request.files:
        current_app.logger.debug("not file send")
        abort(400)

    file = request.files.get('image')
    current_app.logger.debug(type(file))
    current_app.logger.debug(file.filename)
    current_app.logger.debug(request.form)

    current_app.logger.debug("return empy")
    return {}, 400
