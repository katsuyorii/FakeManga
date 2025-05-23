import re

from pydantic import BaseModel, EmailStr, field_validator


class UserRegistrationSchema(BaseModel):
    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, value: str) -> str:
        REGEX_PASSWORD = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&_])[A-Za-z\d@$!%*#?&_]{8,}$"

        if not re.fullmatch(REGEX_PASSWORD, value):
            raise ValueError('Пароль должен содержать минимум 1 букву, 1 цифру и 1 специальный символ и быть не менее 8 символов!')
    
        return value