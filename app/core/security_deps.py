from fastapi import Depends, HTTPException, status, Request, Header
from typing import Optional
from .security_middleware import csrf_protection, validate_request_origin, validate_cookie_integrity
from .config import settings


def validate_csrf_token(
    request: Request,
    x_csrf_token: Optional[str] = Header(None, alias="X-CSRF-Token")
) -> bool:
    if not settings.CSRF_PROTECTION_ENABLED:
        return True
    
    if request.method in {"GET", "HEAD", "OPTIONS", "TRACE"}:
        return True
    
    session_id = _get_session_id(request)
    
    if x_csrf_token:
        if not csrf_protection.validate_csrf_token(x_csrf_token, session_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid CSRF token"
            )
    else:
        pass
    
    return True


def validate_request_security(request: Request) -> bool:
    if not validate_request_origin(request, settings.ALLOWED_ORIGINS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid request origin"
        )
    
    for cookie_name in ["access_token", "session_id", "csrf_token"]:
        if not validate_cookie_integrity(request, cookie_name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid cookie: {cookie_name}"
            )
    
    return True


def get_csrf_token(request: Request) -> str:
    session_id = _get_session_id(request)
    return csrf_protection.generate_csrf_token(session_id)


def _get_session_id(request: Request) -> str:
    auth_header = request.headers.get("authorization")
    if auth_header:
        try:
            from .security import decode_token
            scheme, token = auth_header.split(" ", 1)
            if scheme.lower() == "bearer":
                payload = decode_token(token)
                return payload.get("sub", "")
        except Exception:
            pass
    
    session_cookie = request.cookies.get("session_id")
    if session_cookie:
        return session_cookie
    
    client_ip = request.client.host if request.client else "unknown"
    return f"ip_{client_ip}"


SecurityValidation = Depends(validate_request_security)
CSRFValidation = Depends(validate_csrf_token)
