import uuid
from datetime import timedelta, datetime, timezone
from typing import Dict, Any

import jwt
from jwt import InvalidTokenError
from rest_framework import exceptions

from effective_mobile_task import settings
from user_auth.models import User
from user_auth.token_types import TokenType


def generate_jti() -> str:
    return str(uuid.uuid4())

def sign_token(
        type: str, subject: str,
        payload: Dict[str, Any],
        ttl: timedelta=None
) -> str:
    if not payload:
        payload = {}

    current_timestamp = datetime.now(tz=timezone.utc).timestamp()

    data = dict(
        iss='doshamine',
        sub=subject,
        type=type,
        jti=generate_jti(),
        iat=current_timestamp,
        nbf=payload['nbf'] if payload.get('nbf') else current_timestamp,
    )
    data.update(dict(exp=data['nbf'] + int(ttl.total_seconds()))) if ttl else None
    payload.update(data)

    return jwt.encode(payload=payload, key=settings.SECRET_KEY, algorithm='HS256')


def generate_access_token(
    subject: str,
    payload: Dict[str, Any]=None,
    ttl: timedelta=None
) -> str:
    return sign_token(TokenType.ACCESS.value, subject, payload, ttl)


def generate_refresh_token(
    subject: str,
    payload: Dict[str, Any]=None,
    ttl: timedelta=None
) -> str:
    return sign_token(TokenType.REFRESH.value, subject, payload, ttl)


def verify_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])


def get_sub(token: str) -> str:
    return verify_token(token)['sub']
