from fastapi import Request, Response

from sqlalchemy.ext.asyncio import AsyncSession

from redis.asyncio import Redis

from users.models import UserModel

from .schemas import UserRegistrationSchema, UserLoginSchema, AccessTokenResponseSchema
from .utils import get_user_by_email, get_user_by_id, hashing_password, verify_password, create_access_token, create_refresh_token, verify_jwt_token, set_token_to_blacklist, is_token_to_blacklist
from .exceptions import EMAIL_ALREADY_REGISTERED, INCORRECT_LOGIN_OR_PASSWORD, MISSING_JWT_TOKEN, INVALID_JWT_TOKEN, USER_ACCOUNT_IS_INACTIVE
from .tasks import send_email_task


async def registration(user_data: UserRegistrationSchema, db: AsyncSession) -> None:
    user = await get_user_by_email(user_data.email, db)

    if user is not None:
        raise EMAIL_ALREADY_REGISTERED

    user_data_dict = user_data.model_dump()

    user_data_dict['password'] = hashing_password(user_data_dict.get('password'))

    send_email_task.delay(
    user_data_dict.get('email'),
    "Подтверждение учетной записи",
    "Спасибо за регистрацию на нашем сайте!"
    )

    new_user = UserModel(**user_data_dict)

    db.add(new_user)

async def authentication(user_data: UserLoginSchema, response: Response, db: AsyncSession) -> AccessTokenResponseSchema:
    user = await get_user_by_email(user_data.email, db)

    if not user or not verify_password(user_data.password, user.password):
        raise INCORRECT_LOGIN_OR_PASSWORD
    
    if not user.is_active:
        raise USER_ACCOUNT_IS_INACTIVE
    
    access_token = create_access_token({'sub': str(user.id), 'role': user.role}, response)
    create_refresh_token({'sub': str(user.id)}, response)

    return AccessTokenResponseSchema(access_token=access_token)

async def logout(request: Request, response: Response, redis: Redis) -> None:
    refresh_token = request.cookies.get('refresh_token')

    if not refresh_token:
        raise MISSING_JWT_TOKEN
    
    payload = verify_jwt_token(token=refresh_token)

    await set_token_to_blacklist(redis=redis, token=refresh_token, payload=payload)

    response.delete_cookie(key='access_token')
    response.delete_cookie(key='refresh_token')

async def refresh(request: Request, response: Response, db: AsyncSession, redis: Redis) -> AccessTokenResponseSchema:
    refresh_token = request.cookies.get('refresh_token')

    if not refresh_token:
        raise MISSING_JWT_TOKEN
    
    if await is_token_to_blacklist(redis=redis, token=refresh_token):
        raise INVALID_JWT_TOKEN

    payload = verify_jwt_token(token=refresh_token)
    user_id = payload.get('sub')

    user = await get_user_by_id(int(user_id), db)

    if not user:
        raise INVALID_JWT_TOKEN
    
    if not user.is_active:
        raise USER_ACCOUNT_IS_INACTIVE

    access_token = create_access_token({'sub': user_id, 'role': user.role}, response)
    create_refresh_token({'sub': user_id}, response)

    await set_token_to_blacklist(redis=redis, token=refresh_token, payload=payload)

    return AccessTokenResponseSchema(access_token=access_token)