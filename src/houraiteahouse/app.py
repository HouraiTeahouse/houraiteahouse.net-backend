from flask_api import FlaskAPI
from houraiteahouse.route.request_util import generate_error_response
from .common import extensions
from .config import BaseConfig
from houraiteahouse.route import blueprints, post_process_steps


def create_app(config=BaseConfig):
    app = FlaskAPI(__name__)
    app.config.from_object(config)

    for ext in extensions:
        ext.init_app(app)

    for url, bp in blueprints.items():
        app.register_blueprint(bp, url_prefix=url)

    for step in post_process_steps:
        step(app)

    return app
