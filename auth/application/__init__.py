from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask
import logging

db = SQLAlchemy()
migrate = Migrate()

def create_app(config):
    """Inicializar la aplicación"""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config)

    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    # inicializar otros plugins
    db.init_app(app)
    migrate.init_app(app, db)

    # incluir modulos y rutas
    from application.models.usermodel import User
    from application.views.default import default

    # registrar los blueprints
    app.register_blueprint(default)

    return app
