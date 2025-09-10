from typing import List
from supabase import Client
from fastapi import HTTPException

from ..models.user import User, Role
from ..models.ticket import Ticket, TicketStatus
from ..api.schemas import TicketCreate, TicketUpdate, TicketOut


class TicketService:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    def list_tickets(self, user: User) -> List[TicketOut]:
        """List tickets based on user role"""
        if user.role == Role.ADMIN:
            response = self.supabase.table("tickets").select("*").order("created_at", desc=True).execute()
        else:
            response = self.supabase.table("tickets").select("*").eq("created_by", user.id).order("created_at", desc=True).execute()
        
        tickets = []
        for ticket_data in response.data:
            ticket = Ticket.from_dict(ticket_data)
            tickets.append(TicketOut(
                id=ticket.id,
                title=ticket.title,
                description=ticket.description,
                status=ticket.status,
                priority=ticket.priority,
                created_by=ticket.created_by,
                category_id=ticket.category_id,
                response=ticket.response,
                created_at=ticket.created_at,
                updated_at=ticket.updated_at
            ))
        
        return tickets

    def create_ticket(self, ticket_data: TicketCreate, user: User) -> TicketOut:
        """Create a new ticket"""
        # Validate category exists
        category_response = self.supabase.table("categories").select("*").eq("id", ticket_data.category_id).execute()
        if not category_response.data:
            raise HTTPException(status_code=400, detail="Invalid category")
        
        # Create ticket data
        ticket_dict = {
            "title": ticket_data.title,
            "description": ticket_data.description,
            "category_id": ticket_data.category_id,
            "priority": ticket_data.priority.value,
            "created_by": user.id,
            "status": TicketStatus.open.value
        }
        
        response = self.supabase.table("tickets").insert(ticket_dict).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create ticket")
        
        ticket = Ticket.from_dict(response.data[0])
        return TicketOut(
            id=ticket.id,
            title=ticket.title,
            description=ticket.description,
            status=ticket.status,
            priority=ticket.priority,
            created_by=ticket.created_by,
            category_id=ticket.category_id,
            response=ticket.response,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at
        )

    def get_ticket(self, ticket_id: int, user: User) -> TicketOut:
        """Get ticket by ID with access control"""
        response = self.supabase.table("tickets").select("*").eq("id", ticket_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Not found")
        
        ticket_data = response.data[0]
        ticket = Ticket.from_dict(ticket_data)
        
        # Check access permissions
        if user.role != Role.ADMIN and ticket.created_by != user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        
        return TicketOut(
            id=ticket.id,
            title=ticket.title,
            description=ticket.description,
            status=ticket.status,
            priority=ticket.priority,
            created_by=ticket.created_by,
            category_id=ticket.category_id,
            response=ticket.response,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at
        )

    def update_ticket(self, ticket_id: int, ticket_data: TicketUpdate, user: User) -> TicketOut:
        """Update an existing ticket with access control"""
        # Check if ticket exists
        response = self.supabase.table("tickets").select("*").eq("id", ticket_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Not found")
        
        ticket_dict = response.data[0]
        ticket = Ticket.from_dict(ticket_dict)
        
        # Check access permissions
        if user.role != Role.ADMIN and ticket.created_by != user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        
        # Build update data with role-based restrictions
        update_data = {}
        for field, value in ticket_data.model_dump(exclude_unset=True).items():
            if value is not None:
                # Only admins can update response field
                if field == "response" and user.role != Role.ADMIN:
                    continue
                if field in ["status", "priority"]:
                    update_data[field] = value.value
                else:
                    update_data[field] = value
        
        if not update_data:
            return TicketOut(
                id=ticket.id,
                title=ticket.title,
                description=ticket.description,
                status=ticket.status,
                priority=ticket.priority,
                created_by=ticket.created_by,
                category_id=ticket.category_id,
                response=ticket.response,
                created_at=ticket.created_at,
                updated_at=ticket.updated_at
            )
        
        # Update ticket
        response = self.supabase.table("tickets").update(update_data).eq("id", ticket_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to update ticket")
        
        updated_ticket = Ticket.from_dict(response.data[0])
        return TicketOut(
            id=updated_ticket.id,
            title=updated_ticket.title,
            description=updated_ticket.description,
            status=updated_ticket.status,
            priority=updated_ticket.priority,
            created_by=updated_ticket.created_by,
            category_id=updated_ticket.category_id,
            response=updated_ticket.response,
            created_at=updated_ticket.created_at,
            updated_at=updated_ticket.updated_at
        )

    def close_ticket(self, ticket_id: int) -> TicketOut:
        """Close a ticket (admin only)"""
        # Check if ticket exists
        response = self.supabase.table("tickets").select("*").eq("id", ticket_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Not found")
        
        # Close ticket
        response = self.supabase.table("tickets").update({"status": TicketStatus.closed.value}).eq("id", ticket_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to close ticket")
        
        ticket = Ticket.from_dict(response.data[0])
        return TicketOut(
            id=ticket.id,
            title=ticket.title,
            description=ticket.description,
            status=ticket.status,
            priority=ticket.priority,
            created_by=ticket.created_by,
            category_id=ticket.category_id,
            response=ticket.response,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at
        )

    def delete_ticket(self, ticket_id: int, user: User) -> dict:
        """Delete a ticket with access control"""
        # Check if ticket exists
        response = self.supabase.table("tickets").select("*").eq("id", ticket_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Not found")
        
        ticket_data = response.data[0]
        ticket = Ticket.from_dict(ticket_data)
        
        # Check access permissions
        if user.role != Role.ADMIN and ticket.created_by != user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        
        # Delete ticket
        self.supabase.table("tickets").delete().eq("id", ticket_id).execute()
        return {"ok": True}
