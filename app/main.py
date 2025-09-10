from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from .api import auth, categories, tickets
from .core.security_middleware import SecurityMiddleware
from .core.config import settings
import os

app = FastAPI(
    title="Chamados API",
    description="API para gerenciamento de chamados com autenticação JWT",
    version="1.0.0"
)

# Add security middleware
app.add_middleware(SecurityMiddleware)

# Configure trusted hosts
trusted_hosts = ["localhost", "127.0.0.1", "*.onrender.com"]
if settings.ENV == "prod" or os.getenv("RENDER"):
    trusted_hosts.extend(["*"])  # Allow all hosts in production for now

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=trusted_hosts
)

# Configure CORS with more permissive settings for debugging
cors_origins = settings.ALLOWED_ORIGINS.copy()

# In production, be more permissive for debugging
if settings.ENV == "prod" or os.getenv("RENDER"):
    cors_origins.append("*")  # Temporarily allow all origins for debugging

print(f"🚀 Environment: {settings.ENV}")
print(f"🌐 CORS Origins: {cors_origins}")
print(f"🔧 Render detected: {bool(os.getenv('RENDER'))}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],  # Allow all headers for debugging
    expose_headers=["X-CSRF-Token"]
)

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(tickets.router)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Chamados API - FastAPI + Supabase",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.ENV,
        "render": bool(os.getenv("RENDER")),
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENV,
        "render_detected": bool(os.getenv("RENDER")),
        "cors_origins": settings.ALLOWED_ORIGINS,
        "cors_origins_used": cors_origins,
        "port": os.getenv("PORT", "8000"),
        "host": settings.HOST
    }
