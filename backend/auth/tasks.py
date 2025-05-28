import asyncio
import aiosmtplib

from email.message import EmailMessage

from src.config import settings
from src.celery import celery_app


async def async_send_email(to_email: str, subject: str, body: str) -> None:
    message = EmailMessage()
    message["From"] = settings.SMTP_USER
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        start_tls=True,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
    )

@celery_app.task
def send_email_task(to_email: str, subject: str, body: str) -> None:
    asyncio.run(async_send_email(to_email, subject, body))