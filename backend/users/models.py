from sqlalchemy import text, String
from sqlalchemy.orm import Mapped, mapped_column

from enum import Enum
from datetime import datetime, timezone

from src.database import BaseModel


class UserRoleEnum(str, Enum):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

class UserModel(BaseModel):
    __tablename__ = 'users'

    email: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str]

    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=True)
    role: Mapped[UserRoleEnum] = mapped_column(default=UserRoleEnum.USER, index=True)

    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"), onupdate=lambda: datetime.now(timezone.utc),)

    is_active: Mapped[bool] = mapped_column(default=True)
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_mailing: Mapped[bool] = mapped_column(default=True)