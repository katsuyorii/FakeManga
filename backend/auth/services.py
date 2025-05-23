from sqlalchemy.ext.asyncio import AsyncSession

from users.models import UserModel

from .schemas import UserRegistrationSchema
from .utils import get_user_by_email, hashing_password
from .exceptions import EMAIL_ALREADY_REGISTERED


async def registration(user_data: UserRegistrationSchema, db: AsyncSession) -> None:
    user = await get_user_by_email(user_data.email, db)

    if user is not None:
        raise EMAIL_ALREADY_REGISTERED

    user_data_dict = user_data.model_dump()

    user_data_dict['password'] = await hashing_password(user_data_dict.get('password'))

    new_user = UserModel(**user_data_dict)

    db.add(new_user)
    await db.commit()