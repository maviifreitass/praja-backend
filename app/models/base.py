import enum
from datetime import datetime


class Role(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class TicketStatus(str, enum.Enum):
    open = "open"
    closed = "closed"


class TicketPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"