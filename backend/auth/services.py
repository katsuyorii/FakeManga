from fastapi import Request, Response

from sqlalchemy.ext.asyncio import AsyncSession

from users.models import UserModel
from src.config import settings

from .schemas import UserRegistrationSchema, UserLoginSchema, JWTTokensSchema
from .utils import get_user_by_email, get_user_by_id, hashing_password, verify_password, create_access_token, create_refresh_token, verify_jwt_token
from .exceptions import EMAIL_ALREADY_REGISTERED, INCORRECT_LOGIN_OR_PASSWORD, MISSING_JWT_TOKEN, INVALID_JWT_TOKEN


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
    
    access_token = await create_access_token({'sub': str(user.id), 'role': user.role}, response)
    refresh_token = await create_refresh_token({'sub': str(user.id)}, response)

    return JWTTokensSchema(access_token=access_token, refresh_token=refresh_token)

async def logout(response: Response) -> None:
    response.delete_cookie(key='access_token')
    response.delete_cookie(key='refresh_token')

async def refresh(request: Request, response: Response, db: AsyncSession) -> JWTTokensSchema:
    refresh_token = request.cookies.get('refresh_token')

    if not refresh_token:
        raise MISSING_JWT_TOKEN

    payload = await verify_jwt_token(token=refresh_token)
    user_id = payload.get('sub')

    user = await get_user_by_id(int(user_id), db)

    if not user or not user.is_active:
        raise INVALID_JWT_TOKEN

    access_token = await create_access_token({'sub': user_id, 'role': user.role}, response)
    refresh_token = await create_refresh_token({'sub': user_id}, response)

    return JWTTokensSchema(access_token=access_token, refresh_token=refresh_token)