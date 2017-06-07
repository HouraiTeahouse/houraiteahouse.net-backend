import json
import logging
from flask import Response, request
from functools import wraps

logger = logging.getLogger(__name__)


def generate_response(status, responseBody, mimetype):
    return Response(
        status=status,
        response=responseBody,
        mimetype=mimetype
    )


def generate_success_response(responseBody, mimetype):
    return generate_response(200, responseBody, mimetype)


def generate_error_response(status, responseText):
    return generate_response(
        status,
        json.dumps(
            {
                'message': responseText
            }
        ),
        'application/json'
    )


# Decorator to block requests missing language param that require it
def require_language(field, internalAction, externalAction=None):
    def language_check_wrapper(func):
        @wraps(func)
        def error_on_no_language(*args, **kwargs):
            if field == 'args':
                flag = not (request.args and 'language' in request.args)
            elif field == 'data':
                flag = not (request.data and 'language' in request.data)
            else:
                # NFI how we got here.
                flag = False

            if flag:
                message = 'Language should be specified when {0} ' \
                    'but was not provided'
                logger.debug(message.format(internalAction))
                action = externalAction if externalAction else internalAction
                return generate_error_response(
                    400,
                    message.format(action)
                )

            return func(*args, **kwargs)

        return error_on_no_language
    return language_check_wrapper
