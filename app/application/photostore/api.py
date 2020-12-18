from application import db
from application.photostore.schemas import PhotoCoverageSchema
from application.photostore.models import Photo, PhotoCoverage
from apifairy import arguments, body, response, other_responses
from flask_login import login_required, current_user
from flask import Blueprint
from flask import current_app as app


photostore_api = Blueprint(
    'photos_api', __name__, template_folder='templates')


@photostore_api.route('/v1/photocoverage', methods=['POST'])
@login_required
@body(PhotoCoverageSchema)
@response(PhotoCoverageSchema)
@other_responses({400: 'Invalid request.', 404: 'Photo not found.'})
def create_coverage(data):
    """Crea una cobertura de fotos"""   
    pc = PhotoCoverage(
        headline=data.get('headline'),
        credit_line=data.get('credit_line'),
        excerpt=data.get('excerpt')
    )

    pc.author_id = current_user.id
    pc.keywords = data.get('keywords')
    # agregar las fotos
    for p_id in data.get('photos'):
        photo = Photo.query.get_or_404(p_id)
        pc.photos.append(photo)
    db.session.add(pc)
    db.session.commit()
    return pc

@photostore_api.route('/v1/photocoverage/<id>')
@response(PhotoCoverageSchema)
@other_responses({404: 'Coverage not found'})
def get_coverage(id):
    return {}


@photostore_api.errorhandler(404)
def object_not_found(e):
    return "Object not found", 404
