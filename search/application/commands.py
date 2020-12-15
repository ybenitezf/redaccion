from application.index_shemas import PhotoIndexSchema
from whoosh import index
from flask import Blueprint, current_app as app
from pathlib import Path

cmd = Blueprint('index', __name__)

@cmd.cli.command('create')
def create():
    """Crea los indices de whoosh"""
    base = Path(app.config.get('INDEX_BASE_DIR'))
    base.mkdir(
        parents=True, exist_ok=True)

    app.logger.debug("Creado indice para las fotos en {}".format(
        base / 'photos'
    ))
    photos_dir = base / 'photos'
    photos_dir.mkdir(parents=True, exist_ok=True)
    index.create_in(base / 'photos', PhotoIndexSchema)

