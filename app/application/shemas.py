from application import ma
from application.models.security import User
from application.models.security import Role
from pprint import pprint


class UserSchema(ma.SQLAlchemySchema):

    class Meta:
        model = User

    id = ma.auto_field()
    name = ma.auto_field()
    username = ma.auto_field()
    


class RoleSchema(ma.SQLAlchemySchema):

    class Meta:
        model = Role

    id = ma.auto_field()
    name = ma.auto_field()
    description = ma.auto_field()
