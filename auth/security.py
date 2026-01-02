import datetime
from datetime import timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from jose import jwt, JWTError
from config import settings
from db.session import get_db
from db.models import User

MAX_PASSWORD_LENGTH = 72

# -------------------------
# Password hashing
# -------------------------

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)



def hash_password(password: str) -> str:
    if len(password.encode("utf-8")) > MAX_PASSWORD_LENGTH:
        raise ValueError("Password too long (max 72 bytes)")
    return pwd_context.hash(password)



def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


# -------------------------
# JWT helpers
# -------------------------

def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.datetime.now(datetime.UTC) + timedelta(hours=12),
    }
    return jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_token(token: str) -> int | None:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return int(payload["sub"])
    except JWTError:
        return None


# -------------------------
# FastAPI dependency
# -------------------------

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
