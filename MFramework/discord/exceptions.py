class RequestError(Exception):
    pass

class BadRequest(RequestError):
    pass

class JsonBadRequest(BadRequest):
    pass
