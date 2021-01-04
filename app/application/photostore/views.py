from application import filetools, db
from application.modules.editorjs import renderBlock
from application.permissions import admin_rol
from .forms import SearchPhotosForm
from .models import Photo, PhotoCoverage
from .utiles import StorageController
from .permissions import rol_fotografia, EditPhotoPermission
from whoosh.filedb.filestore import FileStorage
from whoosh.qparser import MultifieldParser
from flask_login import login_required, current_user
from flask_breadcrumbs import register_breadcrumb, default_breadcrumb_root
from flask_menu import register_menu, current_menu
from flask import Blueprint, current_app, render_template, abort
from flask import request, json, send_file
from pathlib import Path
from werkzeug.utils import secure_filename
import os
import tempfile

photostore = Blueprint(
    'photos', __name__, template_folder='templates')
default_breadcrumb_root(photostore, '.')


@photostore.before_app_first_request
def setupMenus():
    navbar = current_menu.submenu("navbar.photostore")
    navbar._external_url = "#!"
    navbar._endpoint = None
    navbar._text = "NAVBAR"

    # mis actions
    actions = current_menu.submenu("actions.photostore")
    actions._text = "Fotos"
    actions._endpoint = None
    actions._external_url = "#!"


@photostore.route('/photo/preview/<id>')
def photo_thumbnail(id):
    p = Photo.query.get_or_404(id)
    return send_file(p.thumbnail)


@photostore.route('/photo/details/<id>')
@register_breadcrumb(photostore, '.index.id', 'Detalles')
def photo_details(id):
    p = Photo.query.get_or_404(id)
    can_edit = (EditPhotoPermission(p.md5).can() or admin_rol.can())
    return render_template(
        'photostore/photo_details.html', foto=p, can_edit=can_edit)


@photostore.route('/')
@register_breadcrumb(photostore, '.index', 'Fotos')
@register_menu(photostore, 'navbar.photostore.index', 'Fotos')
@register_menu(photostore, 'actions.photostore.index', 'Galerias')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    form = SearchPhotosForm()
    coberturas = PhotoCoverage.query.order_by(
        PhotoCoverage.archive_on.desc()).paginate(page, per_page=4)

    return render_template(
        'photostore/index.html', coberturas=coberturas, form=form)


@photostore.route('/myphotos')
@register_breadcrumb(photostore, '.index.mis_fotos', 'Mis fotos')
@register_menu(photostore, 'actions.photostore.mis_fotos', 'Mis fotos')
@login_required
def mis_fotos():
    """Las fotos de este usuario"""
    page = request.args.get('page', 1, type=int)
    form = SearchPhotosForm()
    photos = Photo.query.filter_by(
        upload_by=current_user.id
    ).order_by(
        Photo.archive_on.desc()).paginate(page, per_page=12)
    return render_template(
        'photostore/mis_fotos.html', fotos=photos, search_form=form)


@photostore.route('/search', methods=['GET', 'POST'])
@register_breadcrumb(photostore, '.index.buscar_indice', 'Buscar')
@register_menu(
    photostore, 'actions.photostore.buscar_indice', 'Buscar Fotos')
@login_required
def buscar_indice():
    form = SearchPhotosForm()
    userquery = ""

    if form.validate_on_submit():
        userquery = form.userquery.data

    # hacer la busqueda aqui
    base = Path(current_app.config.get('INDEX_BASE_DIR'))
    store = FileStorage(str(base / 'photos'))
    ix = store.open_index()
    qp = MultifieldParser([
        "headline", "excerpt", "credit_line",
        "taken_by", "keywords"], ix.schema)
    photos = []
    keywords_grp = {}
    with ix.searcher() as s:
        results = s.search(qp.parse(userquery), groupedby="keywords")
        keywords_grp = results.groups("keywords")
        try:
            from_search = [Photo.query.get(r.get('md5')) for r in results]
            # clean up Nones, pueden venir de la busqueda
            photos = [p for p in from_search if p]
        except Exception as e:
            current_app.logger.exception("Hay un problema aqui")

    return render_template(
        'photostore/search.html', form=form,
        fotos=photos, por_keywords=keywords_grp)


@photostore.route('/upload-form')
@register_breadcrumb(photostore, '.index.upload_coverture', 'Subir cobertura')
@register_menu(
    photostore, 'actions.photostore.upload_coverture', 'Subir cobertura')
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
        keywords = json.loads(request.form.get('keywords'))
        user_data = {
            'headline': request.form.get('headline'),
            'creditline': request.form.get('creditline'),
            'keywords': list(filter(None, keywords)),
            'excerpt': request.form.get('excerpt'),
            'uploader': current_user.id,
            'taken_by': request.form.get('takenby')
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


@photostore.context_processor
def render_excerpt_to_html():
    def render_excerpt(in_data):
        data = json.loads(in_data)
        return render_template(
            'photostore/editorjs/photo_except.html', 
            data=data,
            block_rederer=renderBlock)

    return dict(render_excerpt=render_excerpt)
