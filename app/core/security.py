from datetime import datetime, timedelta, timezone
import jwt
from passlib.hash import bcrypt
from .config import settings


def hash_password(raw: str) -> str:
    return bcrypt.hash(raw)


def verify_password(raw: str, hashed: str) -> bool:
    return bcrypt.verify(raw, hashed)


def create_access_token(sub: str, role: str):
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRES_MIN)
    payload = {"sub": sub, "role": role, "exp": expires}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    return token


def decode_token(token: str):
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
