from application import login_mgr, ldap_mgr, db
from application.models.security import User
from application.forms import LoginForm
from flask_login import current_user, login_user, login_required, logout_user
from flask_ldap3_login import AuthenticationResponseStatus
from flask_principal import Identity, AnonymousIdentity, identity_changed
from flask import current_app, Blueprint, jsonify, render_template
from flask import request, redirect, url_for, flash, request, session


users_bp = Blueprint('users', __name__, url_prefix='/users')


@users_bp.route('/profile')
@login_required
def show_user_profile():
    return render_template('users/profile.html', user=current_user)


@login_mgr.user_loader
def load_user(id):
    return User.query.get(id)


@users_bp.route("/logout")
@login_required
def logout():
    logout_user()

    # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        current_app.logger.debug("session.pop({})".format(key))
        session.pop(key, None)

     # Tell Flask-Principal the user is anonymous
    current_app.logger.debug('In logout() identity_changed.send')
    identity_changed.send(
        current_app._get_current_object(), 
        identity=AnonymousIdentity())

    return redirect(url_for('.login'))


@users_bp.route('/login', methods=['GET', 'POST'])
def login():
    next = request.args.get('next')

    if current_user.is_authenticated:
        return redirect(next or url_for('.show_user_profile'))

    form = LoginForm()
    if form.validate_on_submit():
        auth_type = 'database'

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
                auth_type = 'ldap'

        # si no se usa ldap o ya se creo/genero el usuario desde ldap
        # entonces seguir con el flujo normal
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password_hash(form.password.data):
            flash('Nombre de usuario o contraseña incorrectos')
            return redirect(url_for('.login'))
        
        login_user(user)
        # Tell Flask-Principal the identity changed
        identity_changed.send(
            current_app._get_current_object(), 
            identity=Identity(user.id, auth_type=auth_type))
        return redirect(next or url_for('default.index'))

    return render_template('users/login.html', form=form)