import jwt
import bcrypt

from fastapi import Response

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime, timezone, timedelta

from users.models import UserModel
from src.config import settings

from .exceptions import INVALID_JWT_TOKEN, EXPIRED_JWT_TOKEN


async def get_user_by_email(email: str, db: AsyncSession) -> UserModel | None:
    user = await db.execute(select(UserModel).where(UserModel.email == email))

    return user.scalar_one_or_none()

async def get_user_by_id(id: int, db: AsyncSession) -> UserModel | None:
    user = await db.execute(select(UserModel).where(UserModel.id == id))

    return user.scalar_one_or_none()

async def hashing_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)

    return hashed_password.decode()

async def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

async def create_access_token(payload: dict, response: Response) -> str:
    to_encode = payload.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire, 'iat': datetime.now(timezone.utc)})

    access_token = jwt.encode(payload=to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    response.set_cookie(
        key='access_token',
        value=access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=True,
        httponly=True,
        samesite='strict',
    )

    return access_token

async def create_refresh_token(payload: dict, response: Response) -> str:
    to_encode = payload.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({'exp': expire, 'iat': datetime.now(timezone.utc)})

    refresh_token = jwt.encode(payload=to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        secure=True,
        httponly=True,
        samesite='strict',
    )

    return refresh_token

async def verify_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise EXPIRED_JWT_TOKEN
    except jwt.InvalidTokenError:
        raise INVALID_JWT_TOKEN
    
    return payload