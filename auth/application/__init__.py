from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_ldap3_login import LDAP3LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
import logging

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
ldap_mgr = LDAP3LoginManager()
admon = Admin()

def create_app(config):
    """Inicializar la aplicación"""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config)

    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, 
        x_prefix=1)

    # inicializar otros plugins
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    admon.init_app(app)
    ldap_mgr.init_app(app)

    # incluir modulos y rutas
    with app.app_context():
        from application.models.usermodel import User, UserView
        from application.views.default import default

        # registrar los blueprints
        app.register_blueprint(default)
        login.login_view = 'default.log_user'

        # admon views 
        admon.add_view(UserView(User, db.session))

    return app
