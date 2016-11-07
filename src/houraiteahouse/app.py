from flask_api import FlaskAPI
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_cache import Cache
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy_cache import CachingQuery
from .config import BaseConfig

app = FlaskAPI(__name__)
app.config.from_object(BaseConfig)
cors = CORS(app, headers=['Content-Type'])
bcrypt = Bcrypt(app)
db = SQLAlchemy(app, session_options={'query_cls': CachingQuery})
cache = Cache(app)

from .storage import models        # noqa
from .route import auth_route, news_route    # noqa
