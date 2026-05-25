from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from flask import current_app

TOKEN_MAX_AGE_SECONDS = 60 * 60 * 24 * 7  # 7 dage
ALGORITHM = "HS256"


def _secret() -> str:
    return current_app.config["SECRET_KEY"]


def create_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(seconds=TOKEN_MAX_AGE_SECONDS),
    }
    return jwt.encode(payload, _secret(), algorithm=ALGORITHM)


def load_user_id_from_token(token: str) -> Optional[str]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, _secret(), algorithms=[ALGORITHM])
        return payload.get("sub")
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
