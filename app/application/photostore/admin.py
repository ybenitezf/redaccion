from application.views.admin import MySecureModelView
from application.photostore.models import Volume, Media, PhotoCoverage
from application.photostore.models import Photo
from application import db

class VolumeAdminView(MySecureModelView):

    def __init__(self):
        super().__init__(Volume, db.session, category='PhotoStore')


class MediaAdminView(MySecureModelView):

    def __init__(self):
        super().__init__(Media, db.session, category='PhotoStore')


class PhotoCoverageAdminView(MySecureModelView):

    def __init__(self):
        super().__init__(PhotoCoverage, db.session, category='PhotoStore')


class PhotoAdminView(MySecureModelView):
    
    def __init__(self):
        super().__init__(Photo, db.session, category='PhotoStore')
