from flask_api import FlaskAPI
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_cache import Cache
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy_cache import CachingQuery
from .config import BaseConfig

app = FlaskAPI(__name__)
cors = CORS(headers=['Content-Type'])
bcrypt = Bcrypt()
cache = Cache()
db = SQLAlchemy(session_options={'query_cls': CachingQuery})

def create_app(config=BaseConfig):
    app.config.from_object(config)

    cors.init_app(app)
    bcrypt.init_app(app)
    db.init_app(app)
    cache.init_app(app)

    from .storage import models        # noqa
    from .route import auth_route, news_route    # noqa

    return app
