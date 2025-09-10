from fastapi import Request, HTTPException, status
from fastapi.security.utils import get_authorization_scheme_param
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import secrets
import hmac
import hashlib
from typing import Optional
from .config import settings


class SecurityMiddleware(BaseHTTPMiddleware):
    
    def __init__(self, app, csrf_secret: Optional[str] = None):
        super().__init__(app)
        self.csrf_secret = csrf_secret or settings.JWT_SECRET
        self.safe_methods = {"GET", "HEAD", "OPTIONS", "TRACE"}
        
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https://fastapi.tiangolo.com; "
            "connect-src 'self'"
        )
        response.headers["Content-Security-Policy"] = csp_policy
        

        if "set-cookie" in response.headers:
            self._secure_cookies(response)
            
        return response
    
    def _secure_cookies(self, response: Response):
        cookies = response.headers.get("set-cookie", "")
        if cookies:

            secure_flag = "Secure; " if settings.ENV == "production" else ""
            secure_cookies = f"{cookies}; HttpOnly; SameSite=Strict; {secure_flag}Path=/"
            response.headers["set-cookie"] = secure_cookies


class CSRFProtection:
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode()
    
    def generate_csrf_token(self, session_id: str) -> str:
        random_part = secrets.token_urlsafe(32)
        message = f"{session_id}:{random_part}".encode()
        signature = hmac.new(self.secret_key, message, hashlib.sha256).hexdigest()
        return f"{random_part}.{signature}"
    
    def validate_csrf_token(self, token: str, session_id: str) -> bool:
        try:
            if not token or "." not in token:
                return False
                
            random_part, signature = token.rsplit(".", 1)
            message = f"{session_id}:{random_part}".encode()
            expected_signature = hmac.new(self.secret_key, message, hashlib.sha256).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except Exception:
            return False


def validate_request_origin(request: Request, allowed_origins: list = None) -> bool:
    if allowed_origins is None:
        allowed_origins = ["http://localhost:4200", "http://localhost:8000", "https://praja-frontend.onrender.com"]
    
    origin = request.headers.get("origin")
    referer = request.headers.get("referer")
    
    if origin:
        return origin in allowed_origins
    
    if referer:
        for allowed in allowed_origins:
            if referer.startswith(allowed):
                return True
    
    return True


def validate_cookie_integrity(request: Request, cookie_name: str) -> bool:
    cookie_value = request.cookies.get(cookie_name)
    if not cookie_value:
        return True
    
    try:

        if cookie_name == "access_token":
            parts = cookie_value.split(".")
            return len(parts) == 3
        
        return True
    except Exception:
        return False


csrf_protection = CSRFProtection(settings.JWT_SECRET)
