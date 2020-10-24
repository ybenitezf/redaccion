from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_admin import expose
from flask import request, redirect, url_for, current_app
from application import db
from application.models import _gen_uuid


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

    def __repr__(self):
        return '<Role {}>'.format(self.name)


class User(UserMixin, db.Model):
    id = db.Column(db.String(32), primary_key=True, default=_gen_uuid)
    name = db.Column(db.String(120))
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(254), index=True)
    password_hash = db.Column(db.String(128))
    roles = db.relationship(
        'Role', secondary=user_roles, lazy='subquery', 
        backref=db.backref('users', lazy=True))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password_hash(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.email)


