from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_ldap3_login import LDAP3LoginManager
from flask_admin import Admin
from flask_principal import Principal
from flask_debugtoolbar import DebugToolbarExtension
from flask_caching import Cache
from flask_static_digest import FlaskStaticDigest
from flask_logs import LogSetup
from flask_breadcrumbs import Breadcrumbs, register_breadcrumb
from flask_menu import register_menu
from apifairy import APIFairy
from flask_marshmallow import Marshmallow
from celery import Celery
from flask import Flask, redirect
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
import os

logs = LogSetup()
db = SQLAlchemy()
migrate = Migrate()
login_mgr = LoginManager()
ldap_mgr = LDAP3LoginManager()
admon = Admin()
principal = Principal()
devtoolbar = DebugToolbarExtension()
cache = Cache()
flask_statics = FlaskStaticDigest()
apifairy = APIFairy()
ma = Marshmallow()
celery = Celery(__name__)
crumbs = Breadcrumbs()
# Breadcrumbs is a subclass of flask_menu.Menu
menu = crumbs

def create_app(config='config.Config'):
    """Inicializar la aplicación"""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config)
    if os.getenv('APP_CONFIG') and (os.getenv('APP_CONFIG') != config):
        app.config.from_object(os.getenv('APP_CONFIG'))
    logs.init_app(app)

    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, 
        x_prefix=1)

    # inicializar otros plugins
    db.init_app(app)
    migrate.init_app(app, db)
    login_mgr.init_app(app)
    login_mgr.login_message = "Inicie sesión para acceder a esta página"
    if app.config.get('LDAP_AUTH'):
        ldap_mgr.init_app(app)
    principal.init_app(app)
    # devtoolbar.init_app(app)
    cache.init_app(app)
    flask_statics.init_app(app)
    ma.init_app(app)
    crumbs.init_app(app)
    apifairy.init_app(app)
    if app.config.get('CELERY_ENABLED'):
        init_celery(celery, app)

    # incluir modulos y rutas
    with app.app_context():
        from application.views.default import default
        from application.views.users import users_bp
        from application.searchcommands import cmd as search_cmd
        from application.admin_commands import users_cmds
        from application.views.admin import MyAdminIndexView, UserView
        from application.views.admin import RoleView, PermissionView

        admon.init_app(app, index_view=MyAdminIndexView())
        # registrar los blueprints
        app.register_blueprint(default)
        app.register_blueprint(users_bp)
        app.register_blueprint(search_cmd)
        app.register_blueprint(users_cmds)
        login_mgr.login_view = 'users.login'

        # admon views 
        admon.add_view(UserView())
        admon.add_view(RoleView())
        admon.add_view(PermissionView())

        if app.config.get('PHOTOSTORE_ENABLED'):
            from application.photostore import photostore
            from application.photostore import photostore_api
            from application.photostore.admin import VolumeAdminView
            from application.photostore.admin import MediaAdminView
            from application.photostore.admin import PhotoCoverageAdminView
            from application.photostore.admin import PhotoAdminView
            app.register_blueprint(photostore, url_prefix='/photostore')
            app.register_blueprint(
                photostore_api, url_prefix='/photostore/api')
            admon.add_view(VolumeAdminView())
            admon.add_view(MediaAdminView())
            admon.add_view(PhotoCoverageAdminView())
            admon.add_view(PhotoAdminView())

        # the dummy thing
        @app.route("/")
        @register_breadcrumb(app, '.', "Inicio")
        @register_menu(app, '.', "Inicio")
        def home():
            """Registrar una raiz commun para los breadcrumbs"""
            return redirect(url_for('default.index'))

        @app.before_first_request
        def setupMenus():
            """Crear las entradas virtuales del menu"""
            m = menu.root()

            # navbar para el menu principal de la app
            navbar = m.submenu("navbar")
            navbar._external_url = "#!"
            navbar._endpoint = None
            navbar._text = "NAVBAR"

            # actions, para el sidebar, registrar submenus debajo
            # de este menu
            actions = m.submenu("actions")
            actions._external_url = "#!"
            actions._endpoint = None
            actions._text = "NAVBAR"

    return app


def init_celery(instance, app):
    instance.conf.update(app.config)

    class ContextTask(instance.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    instance.Task = ContextTask
