from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
from sqlalchemy import insert, select

from app.db.configuration import get_session
from app.config import client, redis_connection_pool
from app.db.models import User
from app.utils import get_password_hash, generate_token, verify_password
from app.config import settings
from app.db.configuration import redis_connection_pool
from app.schemas.auth import SLoginUser, SRegisterUser


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post('/register', status_code=status.HTTP_200_OK)
async def register_user(user: SRegisterUser, session: AsyncSession = Depends(get_session)):
    query = select(User.id).filter_by(email=user.email)
    result = await session.execute(query)
    finded_user = result.scalar()
    if finded_user:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail='this email is already taken')

    query = insert(User).values(
        fio=user.fio,
        email=user.email,
        password=get_password_hash(user.password)
    ).returning(User.id)
    user = await session.execute(query)
    await session.commit()
    user_id = user.scalar()

    user_token = generate_token(user_id)
    redis = Redis(connection_pool=redis_connection_pool)
    redis.set(str(user_id), user_token)
    return {'token': user_token}
    
    
@router.post('/login', status_code=status.HTTP_200_OK)
async def login_user(user: SLoginUser, session: AsyncSession = Depends(get_session)):
    query = select(User.__table__.columns).filter_by(email=user.email)
    result = await session.execute(query)
    finded_user = result.mappings().one_or_none()
    if not (finded_user and verify_password(user.password, finded_user.password)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='incorrent login or password')

    user_token = generate_token(finded_user.id)
    redis = Redis(connection_pool=redis_connection_pool)
    redis.set(str(finded_user.id), user_token)
    return {'token': user_token}
