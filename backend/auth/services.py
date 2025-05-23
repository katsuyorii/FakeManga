from fastapi import Response

from sqlalchemy.ext.asyncio import AsyncSession

from users.models import UserModel
from src.config import settings

from .schemas import UserRegistrationSchema, UserLoginSchema, JWTTokensSchema
from .utils import get_user_by_email, hashing_password, verify_password, create_access_token, create_refresh_token
from .exceptions import EMAIL_ALREADY_REGISTERED, INCORRECT_LOGIN_OR_PASSWORD


async def registration(user_data: UserRegistrationSchema, db: AsyncSession) -> None:
    user = await get_user_by_email(user_data.email, db)

    if user is not None:
        raise EMAIL_ALREADY_REGISTERED

    user_data_dict = user_data.model_dump()

    user_data_dict['password'] = await hashing_password(user_data_dict.get('password'))

    new_user = UserModel(**user_data_dict)

    db.add(new_user)
    await db.commit()

async def authentication(user_data: UserLoginSchema, response: Response, db: AsyncSession) -> JWTTokensSchema:
    user = await get_user_by_email(user_data.email, db)

    if not user or not await verify_password(user_data.password, user.password):
        raise INCORRECT_LOGIN_OR_PASSWORD
    
    access_token = await create_access_token({'sub': str(user.id), 'role': user.role})
    refresh_token = await create_refresh_token({'sub': str(user.id)})

    response.set_cookie(
        key='access_token',
        value=access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=True,
        httponly=True,
        samesite='strict',
    )

    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        secure=True,
        httponly=True,
        samesite='strict',
    )

    return JWTTokensSchema(access_token=access_token, refresh_token=refresh_token)