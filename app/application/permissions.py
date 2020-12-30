from flask_principal import RoleNeed, Permission

admin_rol = Permission(RoleNeed('admin'))
