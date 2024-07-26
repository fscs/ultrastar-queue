from fastapi import HTTPException, status
from typing import Dict


class EmptySonglistHTTPException(HTTPException):
    _default_status_code: int = status.HTTP_404_NOT_FOUND
    _default_detail: str = "Songlist is empty"

    def __init__(self,
                 status_code: int = _default_status_code,
                 detail: str = _default_detail,
                 headers: Dict[str, str] = None
                 ) -> None:
        self.status_code: int = status_code
        self.detail: str = detail
        self.headers: Dict[str, str] = headers


class NoMatchingSongHTTPException(HTTPException):
    _default_status_code: int = status.HTTP_404_NOT_FOUND
    _default_detail: str = "Could not find songs with provided criteria"

    def __init__(self,
                 status_code: int = _default_status_code,
                 detail: str = _default_detail,
                 headers: Dict[str, str] = None
                 ) -> None:
        self.status_code: int = status_code
        self.detail: str = detail
        self.headers: Dict[str, str] = headers


class SongIdNotMatchingHTTPException(HTTPException):
    _default_status_code: int = status.HTTP_404_NOT_FOUND
    _default_detail: str = "Song_id not found"

    def __init__(self,
                 status_code: int = _default_status_code,
                 detail: str = _default_detail,
                 headers: Dict[str, str] = None
                 ) -> None:
        self.status_code: int = status_code
        self.detail: str = detail
        self.headers: Dict[str, str] = headers
