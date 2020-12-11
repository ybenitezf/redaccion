from flask import current_app as app
from application.photostore.shemas import PhotoCoverageSchema
from apifairy import arguments, body, response, other_responses
from flask import Blueprint

photostore_api = Blueprint(
    'photos_api', __name__, template_folder='templates')


@photostore_api.route('/v1/photocoverage', methods=['POST'])
@body(PhotoCoverageSchema)
@response(PhotoCoverageSchema)
def create_coverage(data):
    """Crea una cobertura de fotos"""
    app.logger.debug(data)
    return data

@photostore_api.route('/v1/photocoverage/<id>')
@response(PhotoCoverageSchema)
@other_responses({404: 'Coverage not found'})
def get_coverage(id):
    return {}
