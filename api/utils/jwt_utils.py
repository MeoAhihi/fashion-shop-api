from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from flask import current_app, request
import jwt


def issue_jwt(user_id: str, email: str) -> str:
    ttl_minutes = int(current_app.config.get("JWT_TTL_MINUTES", 60))
    secret = current_app.config.get("JWT_SECRET")
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ttl_minutes)).timestamp()),
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def require_bearer_token() -> Optional[Dict[str, Any]]:
    secret = current_app.config.get("JWT_SECRET")
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1].strip()
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


