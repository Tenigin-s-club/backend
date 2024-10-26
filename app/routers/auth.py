from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
from sqlalchemy import insert

from app.db.configuration import get_session
<<<<<<< HEAD
from app.config import client
from app.db.models import User
from app.utils import get_password_hash
from app.config import settings
from app.db.configuration import redis_connection_pool
from app.schemas.auth import SLoginUser, SRegisterUser
=======
from app.config import client, settings, redis_connection_pool
from app.db.models import Table_Users
from app.responses import status_200
from app.utiles import Security, Notification
>>>>>>> 7499dd2 (add notification system)


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
    )
    await session.execute(query)
    await session.commit()
<<<<<<< HEAD

    redis = Redis(connection_pool=redis_connection_pool)
    redis.set(user.email, user_token)
    return {'token': user_token}
    
    
@router.post('/login', status_code=status.HTTP_200_OK)
async def login_user(user: SLoginUser):
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

    redis = Redis(connection_pool=redis_connection_pool)
    redis.set(user.email, user_token)
    return {'token': user_token}
=======
    
    
    response_data = response_data.json()
    response.headers.append("Authorization", f"Bearer {response_data["token"]}")
    
    redis = Redis(connection_pool=redis_connection_pool)
    redis.set(user_id, response_data["token"])
    
    response_data.update(
        id = user_id
    )
    return status_200(response_data)
    
    
@router.post("/login")
async def login(text: str, recipient):
    Notification.send_mail("iliakripa@mail.ru", "vlad", "today", "govno", "ochko vlada")
>>>>>>> 7499dd2 (add notification system)
