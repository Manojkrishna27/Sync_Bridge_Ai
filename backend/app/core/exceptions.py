class APIException(Exception):
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

class UnauthorizedException(APIException):
    def __init__(self, message="Unauthorized"):
        super().__init__(message, status_code=401)

class ForbiddenException(APIException):
    def __init__(self, message="Forbidden"):
        super().__init__(message, status_code=403)

class NotFoundException(APIException):
    def __init__(self, message="Not Found"):
        super().__init__(message, status_code=404)
        
class BadRequestException(APIException):
    def __init__(self, message="Bad Request"):
        super().__init__(message, status_code=400)
