import requests
from jose import jwt, JWTError
from fastapi import HTTPException, status

from app.core.config import KEYCLOAK_ISSUER, KEYCLOAK_JWKS_URL


jwks = requests.get(KEYCLOAK_JWKS_URL).json()


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            issuer=KEYCLOAK_ISSUER,
            options={"verify_aud": False}
        )
        return payload

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token not valid"
        )