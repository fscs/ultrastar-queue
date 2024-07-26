from fastapi import HTTPException, status
from typing import Dict


class QueueClosedError(Exception):
    _default_msg: str = "Queue is closed. Can't add any more songs."

    def __init__(self, msg: str = _default_msg) -> None:
        self.msg: str = msg


class QueueClosedHTTPException(HTTPException, QueueClosedError):
    _default_status_code: int = status.HTTP_403_FORBIDDEN
    _default_detail: str = QueueClosedError._default_msg

    def __init__(self,
                 status_code: int = _default_status_code,
                 detail: str = _default_detail,
                 headers: Dict[str, str] = None
                 ) -> None:
        self.status_code: int = status_code
        self.detail: str = detail
        self.headers: Dict[str, str] = headers


class QueueEmptyError(Exception):
    _default_msg: str = "Queue is empty"

    def __init__(self, msg: str = _default_msg) -> None:
        self.msg: str = msg


class QueueEmptyHTTPException(HTTPException, QueueEmptyError):
    _default_status_code: int = status.HTTP_404_NOT_FOUND
    _default_detail: str = QueueEmptyError._default_msg

    def __init__(self,
                 status_code: int = _default_status_code,
                 detail: str = _default_detail,
                 headers: Dict[str, str] = None
                 ) -> None:
        self.status_code: int = status_code
        self.detail: str = detail
        self.headers: Dict[str, str] = headers


class QueueIndexError(Exception):
    _default_msg: str = "Requested index is out of bounds"

    def __init__(self, msg: str = _default_msg) -> None:
        self.msg: str = msg


class QueueIndexHTTPException(HTTPException, QueueIndexError):
    _default_status_code: int = status.HTTP_404_NOT_FOUND
    _default_detail: str = QueueIndexError._default_msg

    def __init__(self,
                 status_code: int = _default_status_code,
                 detail: str = _default_detail,
                 headers: Dict[str, str] = None
                 ) -> None:
        self.status_code: int = status_code
        self.detail: str = detail
        self.headers: Dict[str, str] = headers


class SongNotInDatabaseHTTPException(HTTPException):
    _default_status_code: int = status.HTTP_404_NOT_FOUND
    _default_detail: str = "Song not in database"

    def __init__(self,
                 status_code: int = _default_status_code,
                 detail: str = _default_detail,
                 headers: Dict[str, str] = None
                 ) -> None:
        self.status_code: int = status_code
        self.detail: str = detail
        self.headers: Dict[str, str] = headers


class MismatchingSongDataHTTPException(HTTPException):
    _default_status_code: int = status.HTTP_400_BAD_REQUEST
    _default_detail: str = "Songdata not matching"

    def __init__(self,
                 status_code: int = _default_status_code,
                 detail: str = _default_detail,
                 headers: Dict[str, str] = None
                 ) -> None:
        self.status_code: int = status_code
        self.detail: str = detail
        self.headers: Dict[str, str] = headers
