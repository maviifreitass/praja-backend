from datetime import datetime
from .base import TicketStatus, TicketPriority


class Ticket:
    def __init__(self, id: int, title: str, description: str, status: TicketStatus,
                 created_by: int, category_id: int, priority: TicketPriority = None,
                 response: str = None, created_at: datetime = None, updated_at: datetime = None):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.created_by = created_by
        self.category_id = category_id
        self.priority = priority or TicketPriority.MEDIUM
        self.response = response
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data['id'],
            title=data['title'],
            description=data['description'],
            status=TicketStatus(data['status']),
            created_by=data['created_by'],
            category_id=data['category_id'],
            priority=TicketPriority(data.get('priority', 'MEDIUM')),
            response=data.get('response'),
            created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00')) if data.get('updated_at') else None
        )
