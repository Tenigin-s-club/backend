from passlib.context import CryptContext
from fastapi.security import HTTPBearer
from base64 import urlsafe_b64decode
from json import loads
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from fastapi import status

from app.db.models import User

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from hashlib import sha3_512
import smtplib

from app.config import settings
from app.mail_form import html as mail_form


security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return sha3_512(password.encode()).hexdigest()


async def get_user_id_from_token(token: str, session: AsyncSession) -> UUID:
    try:
        token_payload = token.split('.')[1]
        decoded_payload = urlsafe_b64decode(
            bytes(token_payload, encoding='utf-8')
            + b'=' * (-len(token_payload) % 4)
        ).decode('utf-8')
        user_email = loads(decoded_payload)['sub']
        query = select(User.id).filter_by(email=user_email)
        result = await session.execute(query)
        result = result.mappings().one().get('id')
        
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    return result


class Notification:
    
    @staticmethod
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
