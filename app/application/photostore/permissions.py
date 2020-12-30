from flask_principal import ItemNeed, Permission, RoleNeed

rol_fotografia = Permission(RoleNeed('fotografo'))


class EditPhotoPermission(Permission):
    """Permiso para editar una foto en concreto"""

    def __init__(self, id):
        need = ItemNeed('editar', id, 'foto')
        super(EditPhotoPermission, self).__init__(need)


