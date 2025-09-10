from fastapi import APIRouter, Depends
from datetime import datetime
from . import schemas
from ..models import User
from ..core.deps import get_current_user, require_admin
from ..services.service_factory import get_ticket_service, get_groq_service
from ..services.ticket_service import TicketService
from ..services.groq_service import GroqService
from ..core.config import settings

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("/", response_model=list[schemas.TicketOut])
def list_tickets(
    ticket_service: TicketService = Depends(get_ticket_service), 
    user: User = Depends(get_current_user)
):
    return ticket_service.list_tickets(user)


@router.post("/", response_model=schemas.TicketOut)
def create_ticket(
    payload: schemas.TicketCreate, 
    ticket_service: TicketService = Depends(get_ticket_service), 
    user: User = Depends(get_current_user)
):
    return ticket_service.create_ticket(payload, user)


@router.get("/{tid}", response_model=schemas.TicketOut)
def get_ticket(
    tid: int, 
    ticket_service: TicketService = Depends(get_ticket_service), 
    user: User = Depends(get_current_user)
):
    return ticket_service.get_ticket(tid, user)


@router.put("/{tid}", response_model=schemas.TicketOut)
def update_ticket(
    tid: int, 
    payload: schemas.TicketUpdate, 
    ticket_service: TicketService = Depends(get_ticket_service), 
    user: User = Depends(get_current_user)
):
    return ticket_service.update_ticket(tid, payload, user)


@router.patch("/{tid}/close", response_model=schemas.TicketOut)
def close_ticket(
    tid: int, 
    ticket_service: TicketService = Depends(get_ticket_service), 
    _: User = Depends(require_admin)
):
    return ticket_service.close_ticket(tid)


@router.delete("/{tid}")
def delete_ticket(
    tid: int, 
    ticket_service: TicketService = Depends(get_ticket_service), 
    user: User = Depends(get_current_user)
):
    return ticket_service.delete_ticket(tid, user)


@router.post("/{tid}/ai-response", response_model=schemas.AIResponseOut)
def generate_ai_response(
    tid: int,
    ticket_service: TicketService = Depends(get_ticket_service),
    groq_service: GroqService = Depends(get_groq_service),
    user: User = Depends(get_current_user)
):
    # Get the ticket by ID (no access control for AI responses)
    ticket = ticket_service.get_ticket_by_id(tid)
    
    # Generate AI response using ticket title and description
    ai_response = groq_service.generate_ticket_response(
        title=ticket.title,
        description=ticket.description
    )
    
    return schemas.AIResponseOut(
        response=ai_response,
        used_model=settings.GROQ_MODEL,
        generated_at=datetime.now()
    )