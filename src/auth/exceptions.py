from typing import Dict

from fastapi import HTTPException, status


class CredentialsHTTPException(HTTPException):
    _default_status_code: int = status.HTTP_401_UNAUTHORIZED
    _default_detail: str = "Could not validate credentials"
    _default_headers: Dict[str, str] | None = {"WWW-Authenticate": "Bearer"}

    def __init__(self,
                 status_code: int = _default_status_code,
                 detail: str = _default_detail,
                 headers: Dict[str, str] | None = None
                 ) -> None:
        self.status_code: int = status_code
        self.detail: str = detail
        self.headers: Dict[str, str] = headers if headers else self._default_headers


class NotEnoughPrivilegesHTTPException(HTTPException):
    _default_status_code: int = status.HTTP_401_UNAUTHORIZED
    _default_detail: str = "Not enough privileges"

    def __init__(self, status_code: int = _default_status_code,
                 detail: str = _default_detail,
                 headers: Dict[str, str] | None = None
                 ) -> None:
        self.status_code: int = status_code
        self.detail: str = detail
        self.headers: Dict[str, str] = headers


class AuthenticationHTTPException(HTTPException):
    _default_status_code: int = status.HTTP_401_UNAUTHORIZED
    _default_detail: str = "Incorrect username or password"
    _default_headers: Dict[str, str] = {"WWW-Authenticate": "Bearer"}

    def __init__(self,
                 status_code: int = _default_status_code,
                 detail: str = _default_detail,
                 headers: Dict[str, str] | None = None
                 ) -> None:
        self.status_code: int = status_code
        self.detail: str = detail
        self.headers: Dict[str, str] = headers if headers else self._default_headers
