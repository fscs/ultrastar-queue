from fastapi import HTTPException


class EmptySonglistHTTPException(HTTPException):
    pass


class NoMatchingSongHTTPException(HTTPException):
    pass
