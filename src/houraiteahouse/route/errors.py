from sqlalchemy import exc
from houraiteahouse.route.request_util import generate_error_response

error = Blueprint('error', __name__)


def _error_handler(error_type, status_code, response=None):
    if not response:
        response = lambda err: str(err)

    @error.errorhandler(error_type)
    def error_fun(exception):
        return generate_error_response(status_code, response(exception))
    return error_fun


_error_handler(exc.IntegrityError, 400, response=lambda e: 'Invalid request.')
_error_handler(PermissionError, 403)


# When in debug mode, this handler is bypassed and full stack traces can be
# viewed. In non-debug enviorments, any non-handled exception bubbles up into
# a 500 response, which defaults to this handler.
@error.errorhandler(500)
def unknown_error(exception):
    return generate_error_response(500,
        'An internal error has occured, '
        'please try again later.  '
        'If this error persists, please contact us.'
    )

class InvalidRequestError(Exception):
    status_code = 400
