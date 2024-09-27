from pydantic import BaseModel

# https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#handle-jwt-tokens


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
