from application.models.content import ImageModel
from application import filetools
import tempfile
import urllib
import pathlib
import os
import shutil

def handleImageUpload(filename, user_id, upload_folder):
    """Guardar imagen subida por el usuario

    Si la imagen ya existia retorna la instancia de ImageModel
    que tiene la imagen.
    """
    hash = filetools.md5(filename)
    esta = ImageModel.query.get(hash)

    if esta is not None:
        return esta
    else:
        ext = pathlib.Path(filename).suffix
        dest_filename = "".join([hash, ext])
        full_dest_filename = os.path.join(
            upload_folder, 'images', dest_filename)
        # ensure path exits
        pathlib.Path(
            os.path.join(upload_folder, 'images')
        ).mkdir(parents=True, exist_ok=True)
        # -- 
        with open(filename, mode="rb") as src:
            with open(full_dest_filename, mode="wb") as dst:
                shutil.copyfileobj(src, dst)
        im = ImageModel(
            id=hash, filename=dest_filename, upload_by=user_id)
        return im


def handleURL(url, user_id, upload_folder):
    """Cargar imagen desde una URL

    Esto crea una copia de la imagen en el servidor local
    """
    def _internal_handle(img_uri):
        with urllib.request.urlopen(img_uri) as response:
            ct = response.info()['Content-Type'].split('/')[-1]
            ext = ''.join(['.', ct])
            with tempfile.NamedTemporaryFile(
                    suffix=ext, delete=False) as f:
                shutil.copyfileobj(response, f)

        return f.name

    try:
        fname = _internal_handle(url)
    except UnicodeEncodeError:
        partes = urllib.parse.urlparse(url)
        mpath = urllib.parse.quote(partes.path)
        nurl = urllib.parse.urlunparse((
            partes.scheme, partes.netloc, mpath, partes.params,
            partes.query, partes.fragment
        ))
        fname = _internal_handle(nurl)

    return handleImageUpload(fname, user_id, upload_folder)
