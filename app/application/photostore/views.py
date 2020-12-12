from application.photostore.models import PhotoCoverage
from application.photostore.utiles import StorageController
from application import filetools, db
from flask_login import login_required, current_user
from flask import Blueprint, current_app, render_template, abort
from flask import request, json
from werkzeug.utils import secure_filename
import os
import tempfile

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
@login_required
def handle_upload():
    """Handle uploads from uppy.js"""
    if 'image' not in request.files:
        current_app.logger.debug("not file send")
        abort(400)

    file = request.files.get('image')
    if file.filename == '':
        return {'message': 'Ivalid image'}, 400

    if filetools.allowed_file(file.filename):
        filename = secure_filename(file.filename)
        fullname = os.path.join(tempfile.mkdtemp(), filename)
        file.save(fullname)
        # Procesar la imagen aqui
        # -- 
        keywords = request.form.get('keywords').split(',')
        user_data = {
            'headline': request.form.get('headline'),
            'creditline': request.form.get('creditline'),
            'keywords': list(filter(None, keywords)),
            'excerpt': request.form.get('excerpt'),
            'uploader': current_user.id
        }
        im = StorageController.getInstance().processPhoto(
            fullname, user_data
        )
        if im:
            # retornar la información de la imagen procesada, sobre
            # todo el md5 o id de la imagen
            db.session.add(im)
            db.session.commit()
            return {'md5': im.md5}
        else:
            return {"message": "Invalid image"}, 400
    
    return {"message": "Something went worng"}, 400
