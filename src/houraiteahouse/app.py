from flask.ext.api import FlaskAPI
from flask.ext.cors import CORS
from flask import Response

app = FlaskAPI(__name__)
cors = CORS(app, headers=['Content-Type'])

from . import news

@app.route('/')
def test_call():
    print('Test')
    return Response(status=200)
