from flask_api import FlaskAPI
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask import Response
from .config import BaseConfig

app = FlaskAPI(__name__)
app.config.from_object(BaseConfig)
cors = CORS(app, headers=['Content-Type'])
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

from . import models        # noqa
from . import auth, news    # noqa
