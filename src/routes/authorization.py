from fastapi import APIRouter


router = APIRouter(prefix="auth")

@router.get("/refresh")
async def refresh_token(

):
    pass

@router.post("/register")
async def register():
    pass


@router.post("/login")
async def login():
    pass