from datetime import datetime
from .base import Role


class User:
    def __init__(self, id: int, name: str, email: str, password_hash: str,
                 role: Role, created_at: datetime):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data['id'],
            name=data['name'],
            email=data['email'],
            password_hash=data['password_hash'],
            role=Role(data['role']),
            created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        )
