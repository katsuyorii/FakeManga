from fastapi import APIRouter, Depends, Response, Request, status

from sqlalchemy.ext.asyncio import AsyncSession

from redis.asyncio import Redis

from src.dependencies import get_db, get_redis

from .schemas import UserRegistrationSchema, UserLoginSchema, AccessTokenResponseSchema
from .services import registration, authentication, logout, refresh


auth_router = APIRouter(
    prefix='/auth',
    tags=['Auth'],
)

@auth_router.post('/registration', status_code=status.HTTP_201_CREATED)
async def registration_user(user_data: UserRegistrationSchema, db: AsyncSession = Depends(get_db)):
    await registration(user_data, db)
    return {'message': 'Пользователь успешно зарегестрирован в системе!'}

@auth_router.post('/login', response_model=AccessTokenResponseSchema)
async def login_user(user_data: UserLoginSchema, response: Response, db: AsyncSession = Depends(get_db)):
    return await authentication(user_data, response, db)

@auth_router.post('/logout')
async def logout_user(request: Request, response: Response, redis: Redis = Depends(get_redis)):
    await logout(request, response, redis)
    return {'message': 'Вы успешно вышли из системы!'}

@auth_router.post('/refresh', response_model=AccessTokenResponseSchema)
async def refresh_token(request: Request, response: Response, db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    return await refresh(request, response, db, redis)

@auth_router.get("/redis/all")
async def get_all_redis_with_ttl(redis: Redis = Depends(get_redis)):
    keys = await redis.keys('*')
    values = await redis.mget(*keys) if keys else []

    result = {}
    for k, v in zip(keys, values):
        key_str = k.decode() if isinstance(k, bytes) else str(k)
        val_str = v.decode() if isinstance(v, bytes) else str(v) if v else None
        ttl = await redis.ttl(k)  # время жизни в секундах (-1 если без срока, -2 если нет ключа)
        result[key_str] = {"value": val_str, "ttl": ttl}

    return result