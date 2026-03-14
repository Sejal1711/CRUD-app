from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from app.config.settings import settings


def generate_token(payload: dict) -> str:
    data = payload.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_EXPIRES_DAYS)
    data["exp"] = expire
    return jwt.encode(data, settings.JWT_SECRET, algorithm="HS256")


def verify_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
