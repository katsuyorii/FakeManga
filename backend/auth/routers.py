from fastapi import APIRouter, Depends, Response, Request, status

from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_db

from .schemas import UserRegistrationSchema, UserLoginSchema, JWTTokensSchema
from .services import registration, authentication, logout, refresh


auth_router = APIRouter(
    prefix='/auth',
    tags=['Auth'],
)

@auth_router.post('/registration', status_code=status.HTTP_201_CREATED)
async def registration_user(user_data: UserRegistrationSchema, db: AsyncSession = Depends(get_db)):
    await registration(user_data, db)
    return {'message': 'Пользователь успешно зарегестрирован в системе!'}

@auth_router.post('/login', response_model=JWTTokensSchema)
async def login_user(user_data: UserLoginSchema, response: Response, db: AsyncSession = Depends(get_db)):
    return await authentication(user_data, response, db)

@auth_router.post('/logout')
async def logout_user(response: Response):
    await logout(response)
    return {'message': 'Вы успешно вышли из системы!'}

@auth_router.post('/refresh', response_model=JWTTokensSchema)
async def refresh_token(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    return await refresh(request, response, db)