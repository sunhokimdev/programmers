from rest_framework.views import exception_handler

from myapp.errors import ErrorCodes
from myapp.utils import error_response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data["status_code"] = response.status_code
        response.data["error"] = True

    return error_response(
        ErrorCodes.INVALID_DATA,
        data=response.data,
        status_code=response.status_code.real,
    )
