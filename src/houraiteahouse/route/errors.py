import logging
import sqlite3
from sqlalchemy import exc
from flask import Blueprint
from houraiteahouse.route.request_util import generate_error_response
from werkzeug.exceptions import HTTPException


logger = logging.getLogger(__name__)


def install_error_handlers(app):
    def _error_handler(error_type, status_code, response=None):
        if not response:
            response = lambda err: str(err)
        @app.errorhandler(error_type)
        def error_fun(exception):
            logger.exception(exception)
            return generate_error_response(status_code, response(exception))
        return error_fun

    # _error_handler(exc.IntegrityError, 400, response=lambda e: 'Invalid request.')
    # _error_handler(sqlite3.IntegrityError, 400, response=lambda e: 'Invalid request.')
    # _error_handler(PermissionError, 403)

    def http_error(exception):
        logger.exception(exception)
        return generate_error_response(
                exception.code, '%s - %s' % (str(exception),
                                             exception.description))

    for cls in HTTPException.__subclasses__():
        app.register_error_handler(cls, http_error)

    # When in debug mode, this handler is bypassed and full stack traces can be
    # viewed. In non-debug enviorments, any non-handled exception bubbles up
    # into a 500 response, which defaults to this handler.
    @app.errorhandler(500)
    def unknown_error(exception):
        logger.exception(exception)
        return generate_error_response(500, 'An internal error has occured, '
            'please try again later. If this error persists, please contact us.'
        )


class InvalidRequestError(Exception):
    status_code = 400
