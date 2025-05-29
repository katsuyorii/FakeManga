from fastapi import APIRouter, Depends, Response, Request, status

from sqlalchemy.ext.asyncio import AsyncSession

from redis.asyncio import Redis

from src.dependencies import get_db, get_redis

from .schemas import UserRegistrationSchema, UserLoginSchema, AccessTokenResponseSchema
from .services import registration, authentication, logout, refresh, verify_email


auth_router = APIRouter(
    prefix='/auth',
    tags=['Auth'],
)

@auth_router.post('/registration', status_code=status.HTTP_201_CREATED)
async def registration_user(user_data: UserRegistrationSchema, db: AsyncSession = Depends(get_db)):
    return await registration(user_data, db)

@auth_router.post('/login', response_model=AccessTokenResponseSchema)
async def login_user(user_data: UserLoginSchema, response: Response, db: AsyncSession = Depends(get_db)):
    return await authentication(user_data, response, db)

@auth_router.post('/logout')
async def logout_user(request: Request, response: Response, redis: Redis = Depends(get_redis)):
    return await logout(request, response, redis)

@auth_router.post('/refresh', response_model=AccessTokenResponseSchema)
async def refresh_token(request: Request, response: Response, db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    return await refresh(request, response, db, redis)

@auth_router.get('/email-verify')
async def verify_email_user(token: str, db: AsyncSession = Depends(get_db)):
    return await verify_email(token, db)