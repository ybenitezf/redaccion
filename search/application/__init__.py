from flask import Flask


def create_app(config):
    """Application setup"""
    app = Flask(__name__, instance_relative_config=False)
    # load the config
    app.config.from_object(config)

    with app.app_context():
        # load some plugins, modules or blueprints
        from application.views.api import api

        # registrar los blueprints
        app.register_blueprint(api)

    return app
