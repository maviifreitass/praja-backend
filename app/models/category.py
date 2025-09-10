from datetime import datetime


class Category:
    def __init__(self, id: int, name: str, description: str = None, color: str = None, created_at: datetime = None):
        self.id = id
        self.name = name
        self.description = description
        self.color = color
        self.created_at = created_at

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description'),
            color=data.get('color'),
            created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')) if data.get('created_at') else None
        )
