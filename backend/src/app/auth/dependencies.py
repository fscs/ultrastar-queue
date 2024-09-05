from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

OAuth2PasswordRequestFormDep = Annotated[OAuth2PasswordRequestForm, Depends(OAuth2PasswordRequestForm)]
