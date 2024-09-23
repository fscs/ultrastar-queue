from fastapi import HTTPException


class CredentialsHTTPException(HTTPException):
    pass


class NotEnoughPrivilegesHTTPException(HTTPException):
    pass


class AuthenticationHTTPException(HTTPException):
    pass
