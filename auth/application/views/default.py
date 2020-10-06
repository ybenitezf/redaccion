from application import login
from application.models.usermodel import User
from application.forms import LoginForm
from flask import current_app, Blueprint, jsonify, render_template
from flask import request, redirect, url_for, flash, request
from flask_login import current_user, login_user


default = Blueprint('default', __name__)


@default.route('/')
def index():
    return jsonify(**{'result': 'success'})


@login.user_loader
def load_user(id):
    return User.query.get(id)


@default.route('/login', methods=['GET', 'POST'])
def log_user():
    next = request.args.get('next')

    if current_user.is_authenticated:
        return redirect(next or url_for('default.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password_hash(form.password.data):
            flash('Nombre de usuario o contraseña incorrectos')
            return redirect(url_for('default.log_user'))
        
        login_user(user)
        return redirect(next or url_for('default.index'))

    return render_template('login.html', form=form)
