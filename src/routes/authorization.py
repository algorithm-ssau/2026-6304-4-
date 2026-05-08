from fastapi import APIRouter, Depends

from schemas.authorization.auth_tg import AuthTg
from services.user_service import UserService


router = APIRouter(prefix="auth")

@router.get("/refresh")
async def refresh_token(

):
    pass

@router.post("/register")
async def register(
    body: AuthTg,
    service: UserService = Depends(get_user_service)
):
    pass


@router.post("/login")
async def login():
    pass