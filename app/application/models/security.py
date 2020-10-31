from application import db, cache
from application.models import _gen_uuid
from flask_login import UserMixin, current_user
from flask_admin import expose
from flask_principal import identity_loaded, RoleNeed, UserNeed
from flask import request, redirect, url_for, current_app
from werkzeug.security import generate_password_hash, check_password_hash


user_roles = db.Table(
    'user_roles',
    db.Column(
        'user_id', db.String(32), db.ForeignKey('user.id'), 
        primary_key=True),
    db.Column(
        'role_id', db.String(32), db.ForeignKey('role.id'),
        primary_key=True)
)


class Role(db.Model):
    id = db.Column(db.String(32), primary_key=True, default=_gen_uuid)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    permissions = db.relationship('Permission', lazy='select', backref='role')

    def __repr__(self):
        return '<Role {}>'.format(self.name)


class Permission(db.Model):
    id = db.Column(db.String(32), primary_key=True, default=_gen_uuid)
    # the machine readable permission name
    name = db.Column(db.String(120))
    # the model name if any
    model_name = db.Column(db.String(80))
    # the record id ... empty and the user has access to all record's
    record_id = db.Column(db.String(32))
    # group or role
    role_id =  db.Column(db.String(32), db.ForeignKey('role.id'))

    def __repr__(self):
        return "::".join([self.name, self.model_name, self.record_id])


class User(UserMixin, db.Model):
    id = db.Column(db.String(32), primary_key=True, default=_gen_uuid)
    name = db.Column(db.String(120))
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(254), index=True)
    password_hash = db.Column(db.String(128))
    roles = db.relationship(
        'Role', secondary=user_roles, lazy='select', 
        backref=db.backref('users', lazy=True))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password_hash(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.email)


@identity_loaded.connect
def on_identity_loaded(sender, identity):

    # Set the identity user object
    identity.user = current_user

    if current_user.is_authenticated:
        # Add the UserNeed to the identity
        identity.provides.add(UserNeed(current_user.id))

        # Load the user roles to
        for rol in current_user.roles:
            identity.provides.add(RoleNeed(rol.name))
