from application.permissions import AdminRolNeed
from flask_principal import ItemNeed, Need, Permission, RoleNeed

FotografoRolNeed = RoleNeed('fotografo')

EDIT_PHOTO = 'editar_foto'
CREATE_PHOTO = 'subir_foto'
DOWNLOAD_PHOTO = 'descargar_foto'
TODOS = [EDIT_PHOTO, CREATE_PHOTO, DOWNLOAD_PHOTO]


# Needs sobre todas las fotos
EditarFotosNeed = Need(EDIT_PHOTO, 'foto')
DownloadFotoNeed = Need(DOWNLOAD_PHOTO, 'foto')


class EditPhotoPermission(Permission):
    """Permiso para editar una foto en concreto"""

    def __init__(self, id):
        need = ItemNeed(EDIT_PHOTO, id, 'foto')
        # tiene un permiso directo sobre la foto o es admin
        super(EditPhotoPermission, self).__init__(
            need, AdminRolNeed, EditarFotosNeed)


class DownloadPhotoPermission(Permission):
    """Permiso para descargar las fotos"""

    def __init__(self, id=None):
        needs = [AdminRolNeed, DownloadFotoNeed]
        if id is not None:
            needs.append(ItemNeed(DOWNLOAD_PHOTO, id, 'foto'))
        super().__init__(*needs)
