from application import filetools, db
from application.modules.editorjs import renderBlock
from application.permissions import admin_perm
from .forms import PhotoDetailsForm, SearchPhotosForm
from .models import Photo, PhotoCoverage, PhotoPaginaBusqueda
from .utiles import StorageController
from .permissions import EditPhotoPermission, DownloadPhotoPermission
from .permissions import EDIT_PHOTO, DOWNLOAD_PHOTO
from whoosh.filedb.filestore import FileStorage
from whoosh.qparser import MultifieldParser
from flask_login import login_required, current_user
from flask_breadcrumbs import register_breadcrumb, default_breadcrumb_root
from flask_menu import register_menu, current_menu
from flask import Blueprint, current_app, render_template, abort
from flask import request, json, send_file, request, url_for
from pathlib import Path
from werkzeug.utils import redirect, secure_filename
import os
import tempfile

photostore = Blueprint(
    'photos', __name__, template_folder='templates')
default_breadcrumb_root(photostore, '.')


def can_edit_cobertura(cob: PhotoCoverage):
    return (cob.author_id == current_user.id) or admin_perm.can()

@photostore.context_processor
def photostore_context():
    def can_download(id):
        return DownloadPhotoPermission(id=id).can()

    return {'can_download_photo': can_download}

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


@photostore.route('/photo/getimage/<id>')
def photo_getimage(id):
    p = Photo.query.get_or_404(id)
    return send_file(p.fspath)


@photostore.route('/photo/fakelink/<id>/.<ext>')
def fakelink(id, ext):
    p = Photo.query.get_or_404(id)
    return send_file(p.thumbnail)


@photostore.route('/photo/details/<id>')
@register_breadcrumb(photostore, '.index.id', 'Detalles')
def photo_details(id):
    p = Photo.query.get_or_404(id)
    can_edit = EditPhotoPermission(p.md5)
    return render_template(
        'photostore/photo_details.html', foto=p, can_edit=can_edit)


@photostore.route('/photo/edit/<id>', methods=['GET', 'POST'])
@register_breadcrumb(photostore, '.index.id', 'Editar datos de la foto')
def photo_edit(id):
    p = Photo.query.get_or_404(id)
    can_edit = EditPhotoPermission(p.md5)
    if can_edit is False:
        abort(403)

    form = PhotoDetailsForm()
    if form.validate_on_submit():
        p.headline = form.headline.data
        p.credit_line = form.credit_line.data
        p.excerpt = form.excerpt.data
        p.keywords = json.loads(form.tags.data)
        db.session.add(p)
        db.session.commit()
        # reindexar la foto para que consten los cambios
        StorageController.getInstance().indexPhoto(p)
        return redirect(url_for('.photo_details', id=p.md5))

    return render_template(
        'photostore/photo_edit.html', foto=p, form=form)

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
        'photostore/index.html', coberturas=coberturas, 
        form=form, can_edit=can_edit_cobertura)


def view_editarCobertura_dlc(*args, **kwargs):
    id = request.view_args['id']
    cob = PhotoCoverage.query.get_or_404(id)
    return [
        {
            'text': 'Editar Cobertura', 
            'url': url_for('.editarCobertura', id=cob.id)
        }
    ]


@photostore.route('/editar/cobertura/<id>')
@register_breadcrumb(
    photostore, '.index.editarCobertura', '', 
    dynamic_list_constructor=view_editarCobertura_dlc)
@login_required
def editarCobertura(id):
    cobertura = PhotoCoverage.query.get_or_404(id)
    if can_edit_cobertura(cobertura) is False:
        abort(403)

    return render_template(
        'photostore/editar_cobertura.html', cobertura=cobertura)



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
    userquery = request.args.get('userquery', "")
    try:
        page = int(request.args.get('page' , '1'))
        page = page if page > 0 else 1
    except ValueError:
        page = 1

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
        results = PhotoPaginaBusqueda(s.search_page(
            qp.parse(userquery), page, pagelen=9,  groupedby="keywords"))

    return render_template(
        'photostore/search.html', 
        form=form, results=results,
        userquery=userquery)


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
    """Handle uploads of photos"""
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
            fullname, user_data)
        if im:
            # darle permiso de edición al usuario que sube la foto
            # para que pueda modificiar los datos
            # REVIEW: puede sobre escribir los permisos
            current_user.getUserRole().addPermission(
                EDIT_PHOTO, im.md5, 'foto')
            current_user.getUserRole().addPermission(
                DOWNLOAD_PHOTO, im.md5, 'foto')
            # retornar la información de la imagen procesada, sobre
            # todo el md5 o id de la imagen
            db.session.add(im)
            db.session.commit()
            return {'md5': im.md5}, 200
        else:
            return {"message": "Invalid image"}, 400
    
    return {"message": "Something went worng"}, 400


@photostore.context_processor
def render_excerpt_to_html():
    def render_excerpt(in_data):
        data = json.loads(in_data)
        return render_template(
            'photostore/editorjs/photo_excerpt.html', 
            data=data,
            block_renderer=renderBlock)

    return dict(render_excerpt=render_excerpt)
