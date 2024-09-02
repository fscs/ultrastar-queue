from fastapi import status, HTTPException


def overrides_is_admin_as_false():
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough privileges")
