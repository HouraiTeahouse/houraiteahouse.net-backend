from flask_api import FlaskAPI
from .common import extensions
from .config import BaseConfig
from .route import blueprints

def create_app(config=BaseConfig):
    app = FlaskAPI(__name__)
    app.config.from_object(config)

    for ext in extensions:
        ext.init_app(app)

    for url, bp in blueprints.items():
        app.register_blueprint(bp, url_prefix=url)

    return app
