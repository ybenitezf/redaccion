import shutil
from application import db
from application.models import _gen_uuid
from sqlalchemy.ext.hybrid import hybrid_property, Comparator
from flask import current_app as app
from PIL import Image
from iptcinfo3 import IPTCInfo
from pathlib import Path
from datetime import datetime
import os


DEFAULT_VOL_SIZE = app.config.get('DEFAULT_VOL_SIZE')
DEFAULT_MEDIA_SIZE = app.config.get('DEFAULT_MEDIA_SIZE')

FORMATOS_FECHA = [
    '%Y:%m:%d %H:%M:%S',
    '%Y.%m.%d %H.%M.%S',
    '%Y-%m-%dT%H:%M:%S',
]

def probar_fecha(valor, formatos=FORMATOS_FECHA) -> datetime:
    fecha = None
    valor = valor.strip('\x00')

    for f in formatos:
        try:
            app.logger.debug("Testing format {}".format(f))
            return datetime.strptime(str(valor), f)
        except Exception as e:
            app.logger.exception(
                "{} no esta en formato {}".format(valor, f))

    if fecha is None:
        app.logger.debug(
            "{} fallo todas las pruebas para fecha".format(repr(valor)))

    return fecha


class NewMediaError(Exception):
    pass


class IsInComparator(Comparator):

    def contains(self, other, **kwargs):
        return self.__clause_element__().contains(other)


class Volume(db.Model):
    """A Volume to store photos"""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    capacity = db.Column(db.BigInteger, default=DEFAULT_VOL_SIZE)
    used = db.Column(db.BigInteger, default=0)
    fspath = db.Column(db.Text, default='')
    is_full = db.Column(db.Boolean, default=False)
    medias = db.relationship('Media', backref='volume', lazy=True)


    def storePhoto(
            self, file_name, md5, user_data, size, exif=None) -> 'Photo':
        m = self.findMediaFor(size)

        if m is None:
            # intenta crear un nuevo medio en este volumen
            if self.canStoreBytes(size) and self.canStoreNewMedia():
                m = self.createNewMedia()
            else:
                app.logger.debug(
                    "{} there is not capacity left to store {}".format(
                        self.name, file_name))
                return None

        photo = m.storePhoto(file_name, md5, user_data, size, exif=exif)
        if photo:
            # actualizar la capacidad ocupada
            self.used += size
            self.query.session.add(self)

        return photo

    def canStoreBytes(self, bts) -> bool:
        return (self.used + bts) <= self.capacity

    def _volumeStatus(self) -> tuple:
        actual = Media.query.filter(Media.volume_id == self.id).count()
        soportados = self.capacity / DEFAULT_MEDIA_SIZE
        resto = self.capacity % DEFAULT_MEDIA_SIZE

        return actual, soportados, resto

    def createNewMedia(self) -> 'Media':
        """Try to create a new Media in this volume"""
        actual, soportados, resto = self._volumeStatus()
        capacity = None

        if actual < soportados:
            capacity = DEFAULT_MEDIA_SIZE

        if actual == soportados and resto > 0:
            capacity = resto

        if capacity is None:
            raise NewMediaError

        sess = Media.query.session
        m = Media(volume_id=self.id, capacity=capacity)
        sess.add(m)
        sess.flush()
        m.name = "MEDIA{}".format(m.id)
        m_fspath = os.path.join(self.fspath, m.name)
        Path(m_fspath).mkdir(parents=True, exist_ok=True)
        m.fspath = m_fspath
        sess.add(m)

        return m

    def canStoreNewMedia(self) -> bool:
        """Retorna True si este Volumen puede agregar otro Media"""
        # TODO: Revisar para medios archivados/movidos fuera de Volume
        actual, soportados, resto = self._volumeStatus()

        if actual < soportados:
            return True

        if (actual == soportados) and (resto > 0):
            # ya estan todos pero me queda un poquito para un medio chiquito
            return True

        return False

    def findMediaFor(self, size: int) -> 'Media':
        media_set = Media.query.filter(
            Media.volume_id == self.id).filter(
                Media.is_full.is_(False)).order_by(
                    Media.used.desc())
        for m in media_set:
            if (m.used + size) <= m.capacity:
                return m

        return None

    @classmethod
    def getStorageFor(cls, bts: int) -> 'Volume':
        """Busca un volumen donde guardar file_name"""
        nofull = Volume.query.filter(
            Volume.is_full.is_(False)).order_by(
                Volume.used.desc())
        for v in nofull:
            if v.canStoreBytes(bts):
                return v

        # no se encontro ninguno
        return None

class Media(db.Model):
    """A media to store photos, normally a DVD"""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    capacity = db.Column(db.BigInteger, default=DEFAULT_MEDIA_SIZE)
    used = db.Column(db.BigInteger, default=0)
    fspath = db.Column(db.Text, default='')
    is_full = db.Column(db.Boolean, default=False)
    is_burned = db.Column(db.Boolean, default=False)
    volume_id = db.Column(db.Integer, db.ForeignKey('volume.id'),
        nullable=False)
    photos = db.relationship('Photo', backref='media', lazy=True)


    def storePhoto(
            self, file_name, md5, user_data, size, exif=None) -> 'Photo':
        ext = Path(file_name).suffix
        dest_name = "".join([md5, ext])
        dst = os.path.join(self.fspath, dest_name)
        shutil.copy2(file_name, dst)
        with Image.open(dst) as im:
            width, height = im.size

        tags = user_data.get('keywords')
        photo = Photo(
            md5=md5,
            fspath=dst,
            media_id=self.id,
            image_width=width,
            image_height=height
        )
        photo.keywords = tags
        photo.credit_line = user_data.get('creditline')
        photo.excerpt = user_data.get('excerpt')
        photo.headline = user_data.get('headline')
        photo.upload_by = user_data.get('uploader')

        if exif:
            if 'DateTimeOriginal' in exif:
                # update the date time
                photo.taken_on = probar_fecha(exif['DateTimeOriginal'])
            elif 'DateTimeDigitized' in exif:
                # update the date time
                photo.taken_on = probar_fecha(exif['DateTimeDigitized'])
            elif 'DateTime' in exif:
                photo.taken_on = probar_fecha(exif['DateTime'])

            if 'Artist' in exif:
                photo.taken_by = exif['Artist']
        else:
            # make now the default DateTimeOriginal
            photo.taken_on = datetime.now()

        try:
            info = IPTCInfo(dst)
            if info.get('keywords'):
                tags.extend(info.get('keywords'))
                photo.keywords = tags
        except Exception as e:
            app.logger.debug(
                "Image {} without IPTC info".format(dst))

        app.logger.debug(
            "Updating {}.used from {} to {}".format(
                self.name, self.used, self.used + size))
        self.used = self.used + size
        Media.query.session.add(self)
        Media.query.session.add(photo)

        return photo


gallery = db.Table(
    'photo_galley',
    db.Column(
        'photo_coverage_id', db.String(32),
        db.ForeignKey('photo_coverage.id'),
        primary_key=True),
    db.Column(
        'photo_id', db.String(32), db.ForeignKey('photo.md5'),
        primary_key=True)
)


class Photo(db.Model):
    """A photo in a Media"""

    md5 = db.Column(db.String(32), primary_key=True)
    fspath = db.Column(db.Text, default='')
    thumbnail = db.Column(db.Text, default='')
    archive_on = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    taken_on = db.Column(db.DateTime, index=True, default=None)
    taken_by = db.Column(db.String(100), default='')
    exif_info = db.Column(db.Text, default='')
    image_width = db.Column(db.Integer, default=0)
    image_height = db.Column(db.Integer, default=0)
    archived = db.Column(db.Boolean, default=False)
    _kws = db.Column('keywords', db.Text(), default='')
    upload_by = db.Column(
        db.String(32), db.ForeignKey('user.id'), nullable=True)
    uploader = db.relationship('User', lazy=True)
    media_id = db.Column(db.Integer, db.ForeignKey('media.id'),
        nullable=False)
    credit_line = db.Column(db.String(160), default='')
    excerpt = db.Column(db.Text(), default='')
    headline = db.Column(db.String(512), default='')

    @hybrid_property
    def keywords(self):
        if self._kws is not None:
            return self._kws.split('|')

        return []

    @keywords.setter
    def keywords(self, value):
        self._kws = '|'.join(value)


    @keywords.comparator
    def keywords(cls):
        return IsInComparator(cls._kws)


class PhotoCoverage(db.Model):
    id = db.Column(db.String(32), primary_key=True, default=_gen_uuid)
    headline = db.Column(db.String(512), default='')
    excerpt = db.Column(db.Text(), default='')
    credit_line = db.Column(db.String(160), default='')
    _kws = db.Column('keywords', db.Text(), default='')
    author_id = db.Column(
        db.String(32), db.ForeignKey('user.id'), nullable=True)
    author = db.relationship('User', lazy=True)
    archive_on = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    photos = db.relationship('Photo', secondary=gallery, lazy='subquery')

    @hybrid_property
    def keywords(self):
        if self._kws is not None:
            return self._kws.split('|')

        return []

    @keywords.setter
    def keywords(self, value):
        self._kws = '|'.join(value)


    @keywords.comparator
    def keywords(cls):
        return IsInComparator(cls._kws)



