from fastapi import APIRouter, Depends
from . import schemas
from ..models import User
from ..core.deps import require_admin
from ..services.service_factory import get_category_service
from ..services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])



@router.get("/", response_model=list[schemas.CategoryOut])
def list_categories(
    category_service: CategoryService = Depends(get_category_service)
):
    return category_service.list_categories()


@router.post("/", response_model=schemas.CategoryOut)
def create_category(
    payload: schemas.CategoryCreate, 
    category_service: CategoryService = Depends(get_category_service), 
    _: User = Depends(require_admin)
):
    return category_service.create_category(payload)


@router.get("/{cid}", response_model=schemas.CategoryOut)
def get_category(
    cid: int, 
    category_service: CategoryService = Depends(get_category_service), 
    _: User = Depends(require_admin)
):
    return category_service.get_category(cid)


@router.put("/{cid}", response_model=schemas.CategoryOut)
def update_category(
    cid: int, 
    payload: schemas.CategoryCreate, 
    category_service: CategoryService = Depends(get_category_service), 
    _: User = Depends(require_admin)
):
    return category_service.update_category(cid, payload)


@router.delete("/{cid}")
def delete_category(
    cid: int, 
    category_service: CategoryService = Depends(get_category_service), 
    _: User = Depends(require_admin)
):
    return category_service.delete_category(cid)
