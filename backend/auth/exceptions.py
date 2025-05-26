from fastapi import HTTPException, status


EMAIL_ALREADY_REGISTERED =  HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Данный адрес электронной почты уже зарегестрирован в системе!")

INCORRECT_LOGIN_OR_PASSWORD = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Неправильный логин или пароль!')

USER_ACCOUNT_IS_INACTIVE = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Учетная запись пользователя неактивна!')

EXPIRED_JWT_TOKEN = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Время действия токена истекло!')

INVALID_JWT_TOKEN = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Неверный токен!')

MISSING_JWT_TOKEN = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Отсутствует refresh токен!')