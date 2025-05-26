import jwt
import bcrypt

from fastapi import Response

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from redis.asyncio import Redis

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

def hashing_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)

    return hashed_password.decode()

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

def create_access_token(payload: dict, response: Response) -> str:
    access_token = create_jwt_token(payload=payload, expire_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    set_jwt_cookies(response=response, key='access_token', value=access_token, max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)

    return access_token

def create_refresh_token(payload: dict, response: Response) -> str:
    refresh_token = create_jwt_token(payload=payload, expire_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    set_jwt_cookies(response=response, key='refresh_token', value=refresh_token, max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)

    return refresh_token

def create_jwt_token(payload: dict, expire_delta: timedelta) -> str:
    to_encode = payload.copy()
    datetime_now = datetime.now(timezone.utc)
    expire = datetime_now + expire_delta
    to_encode.update({'exp': expire, 'iat': datetime_now})

    jwt_token = jwt.encode(payload=to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return jwt_token

def set_jwt_cookies(response: Response, key: str, value: str, max_age: int) -> None:
    response.set_cookie(
        key=key,
        value=value,
        max_age=max_age,
        secure=True,
        httponly=True,
        samesite='strict',
    )

def verify_jwt_token(token: str) -> dict:
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

async def set_token_to_blacklist(redis: Redis, token: str, expire_seconds: int) -> None:
    key = f'bl:{token}'
    await redis.set(key, 'true', ex=expire_seconds)

async def is_token_to_blacklist(redis: Redis, token: str) -> bool:
    return await redis.exists(f'bl:{token}')