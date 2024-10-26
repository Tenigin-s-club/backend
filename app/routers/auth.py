from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
from sqlalchemy import insert, select

from app.db.configuration import get_session
from app.config import client, redis_connection_pool
from app.db.models import User
from app.utils import get_password_hash
from app.config import settings
from app.db.configuration import redis_connection_pool
from app.schemas.auth import SLoginUser, SRegisterUser


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post('/register', status_code=status.HTTP_200_OK)
async def register_user(user: SRegisterUser, session: AsyncSession = Depends(get_session)):
    hashed_password = get_password_hash(user.password)
    response = await client.post(
        url=f'{settings.API_ADDRESS}/api/auth/register',
        json={
            'fio': user.fio,
            'email': user.email,
            'password': hashed_password,
            'team': user.team
        }
    )
    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=response.status_code)
    user_token = response.json()['token']

    query = insert(User).values(
        fio=user.fio,
        email=user.email,
        password=hashed_password
    ).returning(User.id)
    user = await session.execute(query)
    await session.commit()

    redis = Redis(connection_pool=redis_connection_pool)
    redis.set(str(user.scalar()), user_token)
    return {'token': user_token}
    
    
@router.post('/login', status_code=status.HTTP_200_OK)
async def login_user(user: SLoginUser, session: AsyncSession = Depends(get_session)):
    hashed_password = get_password_hash(user.password)
    response = await client.post(
        url=f'{settings.API_ADDRESS}/api/auth/login',
        json={
            'email': user.email,
            'password': hashed_password
        }
    )
    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=response.status_code)
    user_token = response.json()['token']

    query = select(User.id).filter_by(email=user.email)
    user = await session.execute(query)

    redis = Redis(connection_pool=redis_connection_pool)
    redis.set(str(user.scalar()), user_token)
    return {'token': user_token}
