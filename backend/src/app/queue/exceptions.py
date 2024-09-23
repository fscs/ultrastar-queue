from fastapi import HTTPException


class NotAValidNumberError(Exception):
    pass


class QueueIndexHTTPException(HTTPException):
    pass


class CantAddSongHTTPException(HTTPException):
    pass


class NotAValidNumberHTTPException(HTTPException):
    pass
