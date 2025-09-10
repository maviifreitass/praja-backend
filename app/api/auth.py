from fastapi import APIRouter, Depends, Request
from . import schemas
from ..models import User
from ..core.deps import get_current_user, require_admin
from ..core.security_deps import SecurityValidation, CSRFValidation, get_csrf_token
from ..services.service_factory import get_auth_service
from ..services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/csrf-token")
def get_csrf_token_endpoint(
    request: Request,
    _: bool = SecurityValidation
):
    csrf_token = get_csrf_token(request)
    return {"csrf_token": csrf_token}


@router.post("/register", response_model=schemas.UserOut)
def register(
    payload: schemas.UserCreate, 
    auth_service: AuthService = Depends(get_auth_service)
):
    return auth_service.register_user(payload)


@router.post("/login", response_model=schemas.TokenOut)
def login(
    form: schemas.LoginRequest, 
    auth_service: AuthService = Depends(get_auth_service),
    _: bool = SecurityValidation
):
    return auth_service.authenticate_user(form.email, form.password)


@router.get("/users", response_model=list[schemas.UserOut])
def get_all_users(
    auth_service: AuthService = Depends(get_auth_service),
    _: User = Depends(require_admin)
):
    return auth_service.get_all_users()


@router.get("/users/{user_id}", response_model=schemas.UserOut)
def get_user_by_id(
    user_id: int,
    auth_service: AuthService = Depends(get_auth_service),
    _: User = Depends(require_admin)
):
    return auth_service.get_user_by_id(user_id)


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    auth_service: AuthService = Depends(get_auth_service),
    _: User = Depends(require_admin),
    __: bool = SecurityValidation,
    ___: bool = CSRFValidation
):
    return auth_service.delete_user(user_id)


@router.get("/me", response_model=schemas.UserOut)
def get_me(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    return auth_service.get_current_user_profile(current_user)


@router.put("/users/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    payload: schemas.UserUpdate,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
    _: bool = SecurityValidation,
    __: bool = CSRFValidation
):
    return auth_service.update_user(user_id, payload, current_user)
