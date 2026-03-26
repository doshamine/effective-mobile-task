import uuid
from datetime import timedelta, datetime, timezone
from typing import Dict, Any, Optional

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from effective_mobile_task import settings
from user_auth.models import RefreshToken, User
from user_auth.token_types import TokenType
from rest_framework import exceptions


def generate_jti() -> str:
    return str(uuid.uuid4())


def get_jti(token: str) -> str:
    payload = get_payload(token)
    return payload.get("jti")


def get_sub(token: str) -> str:
    payload = get_payload(token)
    return payload.get("sub")


def sign_token(
    typ: str,
    subject: str,
    ttl: Optional[timedelta] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> str:
    base = dict(payload or {})
    now = datetime.now(tz=timezone.utc)

    data = dict(
        iss=settings.JWT_ISSUER,
        sub=subject,
        type=typ,
        jti=generate_jti(),
        iat=int(now.timestamp()),
        nbf=base.get("nbf", int(now.timestamp())),
    )

    if ttl is not None:
        exp = now + ttl
        data["exp"] = exp
    base.update(data)

    return jwt.encode(
        payload=base, key=settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def generate_access_token(
    subject: str,
    ttl: Optional[timedelta] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> str:
    return sign_token(TokenType.ACCESS.value, subject, ttl, payload)


def generate_refresh_token(
    subject: str,
    ttl: Optional[timedelta] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> str:
    refresh_token = sign_token(TokenType.REFRESH.value, subject, ttl, payload)
    try:
        user = User.objects.get(pk=subject)
    except User.DoesNotExist:
        raise exceptions.AuthenticationFailed("User not found")
    RefreshToken.objects.create(jti=get_jti(refresh_token), subject=user)
    return refresh_token


def get_payload(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except ExpiredSignatureError:
        raise exceptions.AuthenticationFailed("Token has expired")
    except InvalidTokenError:
        raise exceptions.AuthenticationFailed("Invalid token")


def get_user(token: str) -> User:
    payload = get_payload(token)
    return User.objects.get(pk=payload.get("sub"))


def extract_token(headers: Dict[str, str]) -> str:
    auth_header = headers.get("Authorization")

    if not auth_header:
        raise exceptions.AuthenticationFailed("Authorization header is required")

    if not auth_header.startswith("Bearer "):
        raise exceptions.AuthenticationFailed(
            "Authorization header must start with 'Bearer '"
        )

    token = auth_header.removeprefix("Bearer ").strip()
    return token
