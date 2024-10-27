from datetime import timedelta, datetime, timezone

from passlib.context import CryptContext
from fastapi.security import HTTPBearer
from base64 import urlsafe_b64decode
from json import loads
from jose import jwt
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from fastapi import status
from httpx import Headers

from app.db.models import User
from app.schemas.orders import SOrderInfo
from app.config import client

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

from app.config import settings
from app.mail_form import html as mail_form


security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
token_expiration_time = timedelta(days=1)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def generate_token(user_id: UUID) -> str:
    expire = datetime.now(timezone.utc) + token_expiration_time
    payload = {'exp': expire, 'sub': user_id}
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, settings.ENCODE_ALGORITHM)
    return encoded_jwt


async def get_user_id_from_token(token: str, session: AsyncSession) -> UUID:
    try:
        return jwt.decode(token, settings.SECRET_KEY, settings.ENCODE_ALGORITHM).get('sub')
        query = select(User.id).filter_by(email=user_email)
        result = await session.execute(query)
        return result.mappings().one().get('id')
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


async def new_order(
    order: SOrderInfo,
    token: str
    ) -> int:
    body = {
        "train_id": order.train_id,
        "wagon_id": order.wagon_id,
        "seat_ids": order.seat_ids
    }
    response = await client.post(
        url=f'{settings.API_ADDRESS}/api/order',
        json=body,
        headers=Headers({'Authorization': f'Bearer {token}'})
    )
    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=response.status_code)
    
    order_id = response.json()['order_id']
    return order_id


def send_mail(recipient: str, name, date, living_from, coming_to):
    with smtplib.SMTP_SSL("smtp.mail.ru", 465) as session:
        session.login(settings.MAIL, settings.MAIL_PASSWORD)
        content = mail_form.format(name=name, date=date, living_from=living_from, coming_to=coming_to)

        msg = MIMEMultipart()
        msg["From"] = settings.MAIL
        msg["To"] = recipient
        msg["Subject"] = "Бронь места на поезд"
        msg.attach(MIMEText(content, "html"))

        session.send_message(msg)
        session.quit()
            

