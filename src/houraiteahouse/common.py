from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from .storage.models import db, cache

bcrypt = Bcrypt()
cors = CORS(headers=['Content-Type'])

extensions = [db, cache, bcrypt, cors]
