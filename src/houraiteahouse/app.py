from flask_api import FlaskAPI
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from .storage.models import db, cache
from .config import BaseConfig
from .route import blueprints

cors = None
bcrypt = None


def create_app(config=BaseConfig):
    global cors, bcrypt
    app = FlaskAPI(__name__)
    app.config.from_object(config)
    cors = CORS(app, headers=['Content-Type'])
    bcrypt = Bcrypt(app)

    db.init_app(app)
    cache.init_app(app)

    for url, bp in blueprints.items():
        app.register_blueprint(bp, url_prefix=url)

    return app
