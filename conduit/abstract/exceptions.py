from rest_framework.exceptions import APIException


class BadRequestException(APIException):
    """For raising HTTP_400 Exception"""

    status_code = 400
    default_detail = "Bad Request"
    default_code = "bad_request"


class UnauthorizedException(APIException):
    """For raising HTTP_401 Exception"""

    status_code = 401
    default_detail = "Unauthorized"
    default_code = "unauthorized"
