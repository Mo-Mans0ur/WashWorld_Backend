from typing import Optional

from flask import current_app
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

TOKEN_MAX_AGE_SECONDS = 60 * 60 * 24 * 7  # 7 dage


def _serializer():
    secret = current_app.config["SECRET_KEY"]
    return URLSafeTimedSerializer(secret, salt="washworld-auth")


def create_access_token(user_id: str) -> str:
    return _serializer().dumps({"user_id": user_id})


def load_user_id_from_token(token: str) -> Optional[str]:
    if not token:
        return None
    try:
        data = _serializer().loads(token, max_age=TOKEN_MAX_AGE_SECONDS)
        user_id = data.get("user_id")
        return user_id if user_id else None
    except (BadSignature, SignatureExpired):
        return None
