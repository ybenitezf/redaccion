from application.models.content import ImageModel
from application import filetools
from flask import current_app
from PIL import Image, ImageFilter
import tempfile
import urllib
import pathlib
import os
import shutil


def checkImageSize(file_name):
    _l = current_app.logger.debug

    with Image.open(file_name) as im:
        width, height = im.size
        mode = 'cuadrada'
        mode = 'vertical' if height > width else mode
        mode = 'horizontal' if width > height else mode
        escalar =  False
        if im.format in ['JPEG', 'TIFF']:
            _l("Es JPEG/TIFF")
            _l("La imagen es {}".format(mode))
            if (mode in ['cuadrada', 'horizontal']) and (height > 1080):
                nheight = 1080
                hpercent = (nheight / float(height))
                nwidth = int((float(width) * float(hpercent)))
                escalar = True
            elif (mode == 'vertical') and (width > 900):
                nwidth = 900
                wpercent = (nwidth / float(width))
                nheight = int((float(height) * float(wpercent)))
                escalar = True
            else:
                nwidth, nheight = (width, height)
                _l("No necesita reescalado")

            if escalar is True:
                _l("Nuevas dimensiones {}/{}".format(nwidth, nheight))
                im.thumbnail((nwidth, nheight), resample=Image.BICUBIC)
                _l("Sharpening")
                out = im.filter(ImageFilter.SHARPEN)
                out.save(
                    file_name, format='jpeg', dpi=(72, 72), 
                    quality=95, optimize=True, progressive=True,
                    exif=im.info.get('exif'))
                out.close()
        else:
            _l("formato soportado")


def handleFromPhotoStore(id, original, upload_folder) -> ImageModel:
    """Hacer una copia web de la imagen en photo store

    foto debe ser un registro de Photo en el almacen de fotos
    """
    # 1ro, si ya se realizo una copia de la imagen darla
    # sino, hacer una copia para la web
    _l = current_app.logger.debug

    hash = id
    esta = ImageModel.query.get(hash)
    if esta:
        _l("Ya tenia imagen {}".format(id))
        return esta
    else:
        _l("Copiando de {}".format(original))
        filename = original
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
        # pass
        # resize the image if necesary
        checkImageSize(full_dest_filename)
        r = ImageModel(
            id=hash, filename=dest_filename)
        return r
        # --

def handleImageUpload(hash, filename, user_id, upload_folder):
    """Guardar imagen subida por el usuario

    Si la imagen ya existia retorna la instancia de ImageModel
    que tiene la imagen.
    """
    _l = current_app.logger.debug
    esta = ImageModel.query.get(hash)

    if esta is not None:
        _l("Ya tenia imagen {}".format(hash))
        return esta
    else:
        _l("Copiando nueva imagen")
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
        checkImageSize(full_dest_filename)
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

    hash = filetools.md5(fname)
    return handleImageUpload(hash, fname, user_id, upload_folder)
