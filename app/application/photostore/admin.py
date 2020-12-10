from application.views.admin import MySecureModelView
from application.photostore.models import Volume

class VolumeAdminView(MySecureModelView):

    def __init__(self):
        super().__init__(Volume, Volume.query.session)
