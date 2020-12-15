from flask import Flask


def create_app(config):
    """Application setup"""
    app = Flask(__name__, instance_relative_config=False)
    # load the config
    app.config.from_object(config)

    with app.app_context():
        # load some plugins, modules or blueprints
        from application.api import api
        from application.commands import cmd

        # registrar los blueprints
        app.register_blueprint(api)
        app.register_blueprint(cmd)

    return app
