from fastapi import HTTPException, status


EMAIL_ALREADY_REGISTERED =  HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Данный адрес электронной почты уже зарегестрирован в системе!")