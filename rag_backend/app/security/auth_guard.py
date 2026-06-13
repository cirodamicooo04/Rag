from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from app.security.keycloak import decode_token


security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    return decode_token(token)


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
) -> Optional[dict]:
    if credentials is None:
        return None

    token = credentials.credentials
    return decode_token(token)


def require_role(required_role: str):
    def checker(user: dict = Depends(get_current_user)) -> dict:
        roles = user.get("realm_access", {}).get("roles", [])

        if required_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform this action"
            )

        return user

    return checker
