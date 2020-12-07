from .models import PhotoCoverage
from flask_login import login_required
from flask import Blueprint, current_app, render_template, abort

photostore = Blueprint(
    'photos', __name__, template_folder='templates')


@photostore.route('/')
@login_required
def index():
    current_app.logger.debug(PhotoCoverage.query.all())
    return render_template('photostore/index.html')


@photostore.route('/upload-image', methods=['POST'])
def upload_image():
    abort(400)


@photostore.route('/upload-form')
@login_required
def upload_coverture():
    return render_template('photostore/upload.html')
