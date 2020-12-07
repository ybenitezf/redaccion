from .. import db
from ..models import _gen_uuid
from sqlalchemy.ext.hybrid import hybrid_property, Comparator
from datetime import datetime


DEFAULT_VOL_SIZE = 107374182400
DEFAULT_MEDIA_SIZE = 4831838208


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



