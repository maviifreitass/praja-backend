from typing import List, Optional
from supabase import Client
from fastapi import HTTPException

from ..models.user import User, Role
from ..core.security import hash_password, verify_password, create_access_token
from ..api.schemas import UserCreate, UserUpdate, UserOut, TokenOut


class AuthService:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    def register_user(self, user_data: UserCreate) -> UserOut:
        """Register a new user"""
        # Check if user already exists
        existing_user = self.supabase.table("users").select("*").eq("email", user_data.email).execute()
        if existing_user.data:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user data
        user_dict = {
            "name": user_data.name,
            "email": user_data.email,
            "password_hash": hash_password(user_data.password),
            "role": user_data.role.value,
        }
        
        # Insert user
        response = self.supabase.table("users").insert(user_dict).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        user = User.from_dict(response.data[0])
        return UserOut(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            created_at=user.created_at
        )

    def authenticate_user(self, email: str, password: str) -> TokenOut:
        """Authenticate user and return token"""
        # Find user by email
        response = self.supabase.table("users").select("*").eq("email", email).execute()
        
        if not response.data:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user_data = response.data[0]
        user = User.from_dict(user_data)
        
        # Verify password
        if not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create token
        token = create_access_token(sub=user.email, role=user.role.value)
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": user.role
        }

    def get_all_users(self) -> List[UserOut]:
        """Get all users (admin only)"""
        response = self.supabase.table("users").select("*").order("created_at", desc=True).execute()
        
        users = []
        for user_data in response.data:
            user = User.from_dict(user_data)
            users.append(UserOut(
                id=user.id,
                name=user.name,
                email=user.email,
                role=user.role,
                created_at=user.created_at
            ))
        
        return users

    def get_user_by_id(self, user_id: int) -> UserOut:
        """Get user by ID (admin only)"""
        response = self.supabase.table("users").select("*").eq("id", user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = User.from_dict(response.data[0])
        return UserOut(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            created_at=user.created_at
        )

    def delete_user(self, user_id: int) -> dict:
        """Delete user (admin only)"""
        # Check if user exists
        response = self.supabase.table("users").select("*").eq("id", user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_to_delete = User.from_dict(response.data[0])
        
        # Check if user has tickets
        tickets_response = self.supabase.table("tickets").select("id").eq("created_by", user_id).execute()
        print(tickets_response.data.__str__())
        if tickets_response.data:
            ticket_count = len(tickets_response.data)
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete user: User has {ticket_count} ticket(s) associated. Please resolve or transfer the tickets first."
            )
        
        # Prevent deletion of last admin
        if user_to_delete.role == Role.ADMIN:
            admin_count = self.supabase.table("users").select("id").eq("role", "ADMIN").execute()
            if len(admin_count.data) <= 1:
                raise HTTPException(
                    status_code=400, 
                    detail="Cannot delete the last administrator"
                )
        
        # Delete user
        self.supabase.table("users").delete().eq("id", user_id).execute()
        
        return {
            "message": "User deleted successfully",
            "deleted_user": {
                "id": user_to_delete.id,
                "name": user_to_delete.name,
                "email": user_to_delete.email
            }
        }

    def get_current_user_profile(self, user: User) -> UserOut:
        """Get current user profile"""
        return UserOut(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            created_at=user.created_at
        )

    def update_user(self, user_id: int, user_data: UserUpdate, current_user: User) -> UserOut:
        """Update user information (admin only, or users updating themselves)"""
        # Check if user exists
        response = self.supabase.table("users").select("*").eq("id", user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        existing_user = User.from_dict(response.data[0])
        
        # Authorization: admins can update anyone, users can only update themselves
        if current_user.role != Role.ADMIN and current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Forbidden: You can only update your own profile")
        
        # Build update data from provided fields
        update_data = {}
        for field, value in user_data.model_dump(exclude_unset=True).items():
            if value is not None:
                if field == "email":
                    # Check if new email already exists (but not for same user)
                    email_check = self.supabase.table("users").select("*").eq("email", value).execute()
                    if email_check.data and email_check.data[0]['id'] != user_id:
                        raise HTTPException(status_code=400, detail="Email already in use")
                    update_data[field] = value
                elif field == "password":
                    # Hash the new password
                    update_data["password_hash"] = hash_password(value)
                elif field == "role":
                    # Only admins can change roles
                    if current_user.role != Role.ADMIN and user_data.role == Role.ADMIN :
                        raise HTTPException(status_code=403, detail="Only administrators can change user roles")
                    # Prevent changing the last admin to non-admin
                    if existing_user.role == Role.ADMIN and value != Role.ADMIN:
                        admin_count = self.supabase.table("users").select("id").eq("role", "ADMIN").execute()
                        if len(admin_count.data) <= 1:
                            raise HTTPException(
                                status_code=400, 
                                detail="Cannot change role of the last administrator"
                            )
                    update_data[field] = value.value
                else:
                    update_data[field] = value
        
        if not update_data:
            # No changes to make, return current user data
            return UserOut(
                id=existing_user.id,
                name=existing_user.name,
                email=existing_user.email,
                role=existing_user.role,
                created_at=existing_user.created_at
            )
        
        # Update user
        response = self.supabase.table("users").update(update_data).eq("id", user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to update user")
        
        updated_user = User.from_dict(response.data[0])
        return UserOut(
            id=updated_user.id,
            name=updated_user.name,
            email=updated_user.email,
            role=updated_user.role,
            created_at=updated_user.created_at
        )
