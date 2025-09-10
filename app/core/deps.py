from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from ..database.connection import get_supabase
from .security import decode_token
from ..models.user import User, Role

bearer = HTTPBearer()


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    supabase: Client = Depends(get_supabase)
) -> User:
    try:
        payload = decode_token(creds.credentials)
        email = payload.get("sub")
        if not email:
            raise ValueError("invalid token")
        
        response = supabase.table("users").select("*").eq("email", email).execute()
        
        if not response.data:
            raise ValueError("user not found")
        
        user_data = response.data[0]
        user = User.from_dict(user_data)
        return user
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Admins only")
    return user
