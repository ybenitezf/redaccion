from application.modules.imagetools import handleImageUpload, handleURL
from application.models.content import Article, ImageModel
from application import filetools, db
from flask import Blueprint, jsonify, render_template, request, current_app
from flask import send_from_directory, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from urllib.parse import urlparse
from webpreview import OpenGraph
import tempfile
import os


default = Blueprint('default', __name__)


def allowed_file(filename):
    ALLOWED_EXTENSIONS = current_app.config.get('IMAGES_EXTENSIONS')
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@default.route('/')
@login_required
def index():
    return render_template('default/index.html')


@default.route('/escribir')
def write():
    return render_template('default/write.html')


@default.route('/assets/images/<filename>')
def uploaded_image(filename):
    folder = os.path.join(
        current_app.config['UPLOAD_FOLDER'], "images")
    return send_from_directory(folder, filename)


@default.route('/upload-image', methods=['POST'])
def upload_image():
    """Handler editorjs images"""

    # check if the post request has the file part
    if 'image' not in request.files:
        current_app.logger.debug("No file in request")
        return {"success": 0}

    # if user does not select file, browser also
    # submit an empty part without filename
    file = request.files['image']
    if file.filename == '':
        current_app.logger.debug("Empty file name")
        return {"success": 0}

    if file and allowed_file(file.filename):
        # do the actual thing
        filename = secure_filename(file.filename)
        fullname = os.path.join(tempfile.mkdtemp(), filename)
        file.save(fullname)
        im = handleImageUpload(
            fullname, current_user.id, current_app.config['UPLOAD_FOLDER'])
        db.session.add(im)
        db.session.commit()
        # remove temporary file
        try:
            os.remove(fullname)
        except OSError:
            pass

        return {
            "success": 1,
            "file": {
                "url": url_for(
                    'default.uploaded_image', 
                    filename=im.filename, 
                    _external=True),
                "md5sum": im.id,
            },
            "credit": "Foto de {}".format(im.uploader.name)
        }
    
    current_app.logger.debug("Filename not valid")
    return {"success": 0}


@default.route('/fetch-image', methods=['POST'])
def fetch_image():
    """Download & handle images urls from editorjs"""
    if 'url' not in request.json:
        return {"success": 0}

    url = request.json['url']
    # extract the hostname from url
    if urlparse(url).netloc:
        credit = "Tomada de {}".format(urlparse(url).netloc)
    else:
        credit = "Tomada de Internet"

    try:
        im = handleURL(url, current_user.id, 
            current_app.config['UPLOAD_FOLDER'])
        db.session.add(im)
        db.session.commit()
    except Exception:
        current_app.logger.exception(
            "Can't get the url {}".format(url))
        return {"success": 0}

    return {
        "success": 1,
        "file": {
            "url": url_for(
                'default.uploaded_image', 
                filename=im.filename, 
                _external=True),
            "md5sum": im.id,
        },
        "credit": credit
    }


@default.route('/fetch-link', methods=['GET'])
def fetch_link():
    _l = current_app.logger
    if request.args.get('url'):
        url = request.args.get('url')
        try:
            _l.debug("Retrieving: {}".format(url))
            info = OpenGraph(
                url, [
                    'og:title', 'og:description', 'og:image', 'og:site_name'])
            im = handleURL(
                info.image, current_user.id, 
                current_app.config['UPLOAD_FOLDER'])
            return {
                'success': 1,
                'meta': {
                    'title': info.title,
                    'description': info.description,
                    'site_name': info.site_name,
                    'image': {
                        'url': url_for(
                            'default.uploaded_image', 
                            filename=im.filename, 
                            _external=True),
                        'md5sum': im.id
                    }
                }
            }
        except Exception as e:
            _l.exception("Ocurrio un error procesando el enlace")
            return {'success': 0}

    return {"success" : 0}
