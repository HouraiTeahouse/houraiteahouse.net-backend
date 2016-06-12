from flask.ext.api import FlaskAPI
from flask.ext.cors import CORS
from flask.ext.bcrypt import Bcrypt
from flask.ext.sqlalchemy import SQLAlchemy
from flask import Response
from .config import BaseConfig

app = FlaskAPI(__name__)
app.config.from_object(BaseConfig)
cors = CORS(app, headers=['Content-Type'])
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

from . import models
from . import authentication, news
