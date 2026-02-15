from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm
from db.session import get_db
from db.models import User
from auth.security import (
    hash_password,
    verify_password,
    create_access_token,
)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup")
async def signup(
    username: str,
    password: str,
    db: AsyncSession = Depends(get_db),
):
    print("PASSWORD RECEIVED:", repr(password))
    print("BYTE LENGTH:", len(password.encode("utf-8")))
    try:
        hashed_password = hash_password(password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    result = await db.execute(
        select(User).where(User.username == username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(
        username=username,
        password_hash=hashed_password,
    )
    db.add(user)
    await db.commit()

    return {"message": "User created"}


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.username == form_data.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer"
    }