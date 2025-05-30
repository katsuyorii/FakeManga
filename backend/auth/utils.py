import jwt
import bcrypt

from fastapi import Response

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from redis.asyncio import Redis

from jinja2 import Environment, FileSystemLoader

from datetime import datetime, timezone, timedelta

from users.models import UserModel
from src.config import settings

from .exceptions import INVALID_JWT_TOKEN, EXPIRED_JWT_TOKEN


env = Environment(loader=FileSystemLoader("templates"))

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
    access_token = create_jwt_token(payload, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    set_jwt_cookies(response, 'access_token', access_token, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)

    return access_token

def create_refresh_token(payload: dict, response: Response) -> str:
    refresh_token = create_jwt_token(payload, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    set_jwt_cookies(response, 'refresh_token', refresh_token, settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)

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

async def set_token_to_blacklist(redis: Redis, token: str, payload: dict) -> None:
    key = f'blacklist:{token}'
    expire_token = payload.get('exp')
    datetime_now = int(datetime.now(timezone.utc).timestamp())
    ttl = expire_token - datetime_now
    
    await redis.set(key, 'true', ex=ttl)

async def is_token_to_blacklist(redis: Redis, token: str) -> bool:
    return await redis.exists(f'blacklist:{token}')

def create_verify_email_message(user_id: int) -> str:
    verify_token = create_jwt_token(payload={'sub': str(user_id)}, expire_delta=timedelta(minutes=settings.EMAIL_VERIFY_EXPIRE_MINUTES))
    message = render_verify_email_message_html(verify_token)

    return message

def render_verify_email_message_html(token: str) -> str:
    template = env.get_template("verify_email.html")
    verify_link = f"http://127.0.0.1:8000/auth/email-verify?token={token}"
    
    return template.render(verify_link=verify_link)