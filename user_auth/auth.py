import uuid
from datetime import timedelta, datetime, timezone
from typing import Dict, Any

import jwt

from effective_mobile_task import settings
from user_auth.models import RefreshToken, User
from user_auth.token_types import TokenType


def generate_jti() -> str:
    return str(uuid.uuid4())


def get_jti(token: str) -> str:
    payload = get_payload(token)
    return payload["jti"]


def sign_token(
    type: str, subject: str, ttl: timedelta = None, payload: Dict[str, Any] = None
) -> str:
    if not payload:
        payload = {}

    current_timestamp = datetime.now(tz=timezone.utc).timestamp()

    data = dict(
        iss=settings.JWT_ISSUER,
        sub=subject,
        type=type,
        jti=generate_jti(),
        iat=current_timestamp,
        nbf=payload["nbf"] if payload.get("nbf") else current_timestamp,
    )
    data.update(dict(exp=data["nbf"] + int(ttl.total_seconds()))) if ttl else None
    payload.update(data)

    return jwt.encode(payload=payload, key=settings.SECRET_KEY, algorithm="HS256")


def generate_access_token(
    subject: str, ttl: timedelta = None, payload: Dict[str, Any] = None
) -> str:
    return sign_token(TokenType.ACCESS.value, subject, ttl, payload)


def generate_refresh_token(
    subject: str, ttl: timedelta = None, payload: Dict[str, Any] = None
) -> str:
    refresh_token = sign_token(TokenType.REFRESH.value, subject, ttl, payload)
    user = User.objects.get(pk=subject)
    RefreshToken.objects.create(jti=get_jti(refresh_token), subject=user)
    return refresh_token


def get_payload(token: str) -> Dict[str, Any]:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
