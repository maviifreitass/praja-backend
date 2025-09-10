from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from .api import auth, categories, tickets
from .core.security_middleware import SecurityMiddleware
from .core.config import settings

app = FastAPI(
    title="Chamados API",
    description="API para gerenciamento de chamados com autenticação JWT",
    version="1.0.0"
)

app.add_middleware(SecurityMiddleware)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.onrender.com"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token", "X-Requested-With"],
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
        "docs": "/docs",
        "redoc": "/redoc"
    }
