import json
from flask import Response

# Not necessarily a TODO, but maybe write common request handler logic (such as a call wrapper or decorator with common error handling etc)

def generate_response(status, responseBody, mimetype):
    return Response (
        status = status,
        response = responseBody,
        mimetype = mimetype
    )


def generate_success_response(responseBody, mimetype):
    return generate_response(200, responseBody, mimetype)


def generate_error_response(status, responseText):
    return generate_response(status, json.dumps({'message': responseText}), 'application/json')
