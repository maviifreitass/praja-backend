from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from . import schemas
from ..models import User
from ..core.deps import get_current_user, require_admin
from ..services.service_factory import get_groq_service
from ..services.groq_service import GroqService
from ..core.config import settings

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/generate-response", response_model=schemas.AIResponseOut)
def generate_ai_response(
    payload: schemas.AIResponseRequest,
    groq_service: GroqService = Depends(get_groq_service),
    _: User = Depends(get_current_user)  # Authentication required
):
    """
    Generate an AI-powered response from title and description
    
    This endpoint allows generating AI responses for support queries using Groq AI.
    Perfect for getting automated responses for tickets or general support questions.
    
    Access: Any authenticated user
    """
    ai_response = groq_service.generate_ticket_response(
        title=payload.title,
        description=payload.description
    )
    
    return schemas.AIResponseOut(
        response=ai_response,
        used_model=settings.GROQ_MODEL,
        generated_at=datetime.now()
    )


@router.get("/health")
def ai_health_check(
    groq_service: GroqService = Depends(get_groq_service),
    _: User = Depends(require_admin)  # Admin only
):
    """
    Check the health status of the AI service
    
    Returns the status of the Groq AI integration.
    Useful for monitoring and debugging.
    
    Access: Admin only
    """
    try:
        is_healthy = groq_service.health_check()
        
        if not is_healthy:
            raise HTTPException(
                status_code=503,
                detail="AI service is not responding properly"
            )
        
        return {
            "status": "healthy",
            "service": "groq",
            "model": settings.GROQ_MODEL,
            "checked_at": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"AI service health check failed: {str(e)}"
        )

