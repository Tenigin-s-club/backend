from passlib.context import CryptContext
from fastapi.security import HTTPBearer
from base64 import urlsafe_b64decode
from json import loads
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def get_user_id_from_token(token: str, session: AsyncSession) -> UUID:
    token_payload = token.split('.')[1]
    decoded_payload = urlsafe_b64decode(
        bytes(token_payload, encoding='utf-8')
        + b'=' * (-len(token_payload) % 4)
    ).decode('utf-8')
    user_email = loads(decoded_payload)['sub']
    query = select(User.id).filter_by(email=user_email)
    result = await session.execute(query)
    return result.mappings().one().get('id')
