from application import login, ldap_mgr, db
from application.models.usermodel import User
from application.forms import LoginForm
from flask import current_app, Blueprint, jsonify, render_template
from flask import request, redirect, url_for, flash, request
from flask_login import current_user, login_user, login_required, logout_user
from flask_ldap3_login import AuthenticationResponseStatus


default = Blueprint('default', __name__)


@default.route('/')
def index():
    return jsonify(**{'result': 'success'})

@default.route('/profile')
@login_required
def show_user_profile():
    return render_template('profile.html', user=current_user)


@login.user_loader
def load_user(id):
    return User.query.get(id)


@default.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('default.log_user'))


@default.route('/login', methods=['GET', 'POST'])
def log_user():
    next = request.args.get('next')

    if current_user.is_authenticated:
        return redirect(next or url_for('default.index'))

    form = LoginForm()
    if form.validate_on_submit():

        if current_app.config['LDAP_AUTH']:
            # cargar usuario desde LDAP
            # crearlo/actualizar sus datos si no esta en mi base de datos
            res = ldap_mgr.authenticate(
                form.username.data, form.password.data)
            if res.status is AuthenticationResponseStatus.success:
                # crear/actualizar usuario
                user = User.query.filter_by(
                    username=form.username.data).first()
                if user is None:
                    user = User()

                user.name = res.user_info['displayName']
                user.set_password(form.password.data)
                user.username = res.user_info['sAMAccountName']
                user.email = res.user_info['mail']
                db.session.add(user)
                db.session.commit()

        # si no se usa ldap o ya se creo/genero el usuario desde ldap
        # entonces seguir con el flujo normal
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password_hash(form.password.data):
            flash('Nombre de usuario o contraseña incorrectos')
            return redirect(url_for('default.log_user'))
        
        login_user(user)
        return redirect(next or url_for('default.index'))

    return render_template('login.html', form=form)
