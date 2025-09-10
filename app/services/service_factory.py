from fastapi import Depends
from supabase import Client

from ..database.connection import get_supabase
from .auth_service import AuthService
from .category_service import CategoryService
from .ticket_service import TicketService


def get_auth_service(supabase: Client = Depends(get_supabase)) -> AuthService:
    """Dependency to get AuthService instance"""
    return AuthService(supabase)


def get_category_service(supabase: Client = Depends(get_supabase)) -> CategoryService:
    """Dependency to get CategoryService instance"""
    return CategoryService(supabase)


def get_ticket_service(supabase: Client = Depends(get_supabase)) -> TicketService:
    """Dependency to get TicketService instance"""
    return TicketService(supabase)
