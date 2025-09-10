from typing import List
from supabase import Client
from fastapi import HTTPException

from ..models.category import Category
from ..api.schemas import CategoryCreate, CategoryOut


class CategoryService:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    def list_categories(self) -> List[CategoryOut]:
        """List all categories"""
        response = self.supabase.table("categories").select("*").order("created_at", desc=True).execute()
        
        categories = []
        for cat_data in response.data:
            cat = Category.from_dict(cat_data)
            categories.append(CategoryOut(
                id=cat.id,
                name=cat.name,
                description=cat.description or "Categoria",
                color=cat.color or "#3b82f6",
                created_at=cat.created_at
            ))
        
        return categories

    def create_category(self, category_data: CategoryCreate) -> CategoryOut:
        """Create a new category"""
        # Check if category already exists
        existing = self.supabase.table("categories").select("*").eq("name", category_data.name).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="Category exists")
        
        # Create category data
        cat_dict = {
            "name": category_data.name,
            "description": category_data.description,
            "color": category_data.color
        }
        response = self.supabase.table("categories").insert(cat_dict).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create category")
        
        cat = Category.from_dict(response.data[0])
        return CategoryOut(
            id=cat.id,
            name=cat.name,
            description=cat.description,
            color=cat.color,
            created_at=cat.created_at
        )

    def get_category(self, category_id: int) -> CategoryOut:
        """Get category by ID"""
        response = self.supabase.table("categories").select("*").eq("id", category_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Not found")
        
        cat = Category.from_dict(response.data[0])
        return CategoryOut(
            id=cat.id,
            name=cat.name,
            description=cat.description,
            color=cat.color,
            created_at=cat.created_at
        )

    def update_category(self, category_id: int, category_data: CategoryCreate) -> CategoryOut:
        """Update an existing category"""
        # Check if category exists
        existing = self.supabase.table("categories").select("*").eq("id", category_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Not found")
        
        # Update category data
        update_data = {
            "name": category_data.name,
            "description": category_data.description,
            "color": category_data.color
        }
        response = self.supabase.table("categories").update(update_data).eq("id", category_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to update category")
        
        cat = Category.from_dict(response.data[0])
        return CategoryOut(
            id=cat.id,
            name=cat.name,
            description=cat.description,
            color=cat.color,
            created_at=cat.created_at
        )

    def delete_category(self, category_id: int) -> dict:
        """Delete a category"""
        # Check if category exists
        existing = self.supabase.table("categories").select("*").eq("id", category_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Not found")
        
        # Delete category
        self.supabase.table("categories").delete().eq("id", category_id).execute()
        return {"ok": True}
