from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_admin.contrib.sqla import ModelView
from flask_admin import expose
from flask import request, redirect, url_for, current_app
from application import db
from application.models import _gen_uuid
from application.forms import NewUserForm


class User(UserMixin, db.Model):
    id = db.Column(db.String(32), primary_key=True, default=_gen_uuid)
    name = db.Column(db.String(120))
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(254), index=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password_hash(self, password):
        return check_password_hash(self.password_hash, password)


class UserView(ModelView):

    @expose('/new/', methods=['GET', 'POST'])
    def create_view(self):
        form = NewUserForm()

        if form.validate_on_submit():
            u = User()
            u.username = form.username.data
            u.name = form.name.data
            u.email = form.email.data
            u.set_password(form.password1.data)
            db.session.add(u)
            db.session.commit()
            if '_add_another' in request.form:
                return redirect(url_for('user.create_view'))
            else:
                return redirect(url_for('user.index_view'))


        return self.render('create_user.html', form=form)
