from pydantic import BaseModel, EmailStr, Field, validator, field_validator
from typing import Optional
from datetime import datetime
import re
from ..models.base import Role, TicketStatus, TicketPriority


class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    
    @field_validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Nome é obrigatório')
        v = re.sub(r'\s+', ' ', v.strip())
        if not re.match(r'^[a-zA-ZÀ-ÿ\s]+$', v):
            raise ValueError('Nome deve conter apenas letras e espaços')
        return v
    
    @field_validator('email')
    def validate_email(cls, v):
        if not v:
            raise ValueError('Email é obrigatório')
        suspicious_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com']
        domain = v.split('@')[1].lower()
        if domain in suspicious_domains:
            raise ValueError('Domínio de email não permitido')
        return v.lower()


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    role: Role = Field(default=Role.USER)
    
    @field_validator('password')
    def validate_password(cls, v):
        if not v:
            raise ValueError('Senha é obrigatória')
        if len(v) < 6:
            raise ValueError('Senha deve ter pelo menos 6 caracteres')
        common_passwords = ['password', '123456789', 'qwerty', 'admin123']
        if v.lower() in common_passwords:
            raise ValueError('Senha muito comum, escolha uma mais segura')
        return v


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=128)
    role: Optional[Role] = None
    
    @field_validator('name')
    def validate_name(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Nome é obrigatório')
            v = re.sub(r'\s+', ' ', v.strip())
            if not re.match(r'^[a-zA-ZÀ-ÿ\s]+$', v):
                raise ValueError('Nome deve conter apenas letras e espaços')
        return v
    
    @field_validator('email')
    def validate_email(cls, v):
        if v is not None:
            if not v:
                raise ValueError('Email é obrigatório')
            suspicious_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com']
            domain = v.split('@')[1].lower()
            if domain in suspicious_domains:
                raise ValueError('Domínio de email não permitido')
            v = v.lower()
        return v
    
    @field_validator('password')
    def validate_password(cls, v):
        if v is not None:
            if not v:
                raise ValueError('Senha é obrigatória')
            if len(v) < 6:
                raise ValueError('Senha deve ter pelo menos 6 caracteres')
            common_passwords = ['password', '123456789', 'qwerty', 'admin123']
            if v.lower() in common_passwords:
                raise ValueError('Senha muito comum, escolha uma mais segura')
        return v


class UserOut(UserBase):
    id: int
    role: Role
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = Field(default="bearer")
    role: Role


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: str = Field(None, max_length=500)
    color: str = Field(..., min_length=7, max_length=7)
    
    @field_validator('name')
    def validate_category_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Nome da categoria é obrigatório')
        v = re.sub(r'\s+', ' ', v.strip())
        if not re.match(r'^[a-zA-ZÀ-ÿ0-9\s\-_]+$', v):
            raise ValueError('Nome da categoria contém caracteres inválidos')
        return v

    @field_validator('description')
    def validate_description(cls, v):
        return v
    
    @field_validator('color')
    def validate_color(cls, v):
        if not v:
            raise ValueError('Cor é obrigatória')
        if not re.match(r'^#[0-9a-fA-F]{6}$', v):
            raise ValueError('Cor deve estar no formato hexadecimal (#RRGGBB)')
        return v.lower()


class CategoryCreate(CategoryBase):
    pass


class CategoryOut(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TicketBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    category_id: int = Field(..., gt=0)
    priority: TicketPriority
    
    @field_validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Título é obrigatório')
        v = re.sub(r'\s+', ' ', v.strip())
        if not re.search(r'[a-zA-ZÀ-ÿ0-9]', v):
            raise ValueError('Título deve conter pelo menos letras ou números')
        return v
    
    @field_validator('description')
    def validate_description(cls, v):
        if not v or not v.strip():
            raise ValueError('Descrição é obrigatória')
        return v

class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    response: Optional[str] = None


class TicketOut(BaseModel):
    id: int
    title: str
    description: str
    status: TicketStatus
    priority: TicketPriority
    created_by: int
    category_id: int
    response: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# AI Response Schemas
class AIResponseRequest(BaseModel):
    """Request schema for AI response generation"""
    title: str = Field(min_length=1, max_length=200, description="Ticket title")
    description: str = Field(min_length=1, max_length=2000, description="Ticket description")


class AIResponseOut(BaseModel):
    """Response schema for AI generated response"""
    response: str = Field(description="AI generated response")
    used_model: str = Field(description="AI model used for generation")
    generated_at: datetime = Field(description="Timestamp when response was generated")
