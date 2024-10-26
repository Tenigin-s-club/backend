from fastapi import APIRouter, Depends, Response
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
from sqlalchemy import insert, select

from app.schemas.auth import *
from app.db.configuration import get_session
from app.config import client, settings, redis_connection_pool
from app.db.models import Table_Users
from app.responses import status_200
from app.utiles import Security


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post("/register")
async def register(user_data: RegisterSchema, response: Response, session: AsyncSession = Depends(get_session)):
    
    user_data.password = Security.encode_password(user_data.password)
    body = { 
        "fio": user_data.fio,
        "email": user_data.email,
        "password": user_data.password,
        "team": user_data.team
    }
    response_data = await client.post(settings.API_ADDRESS + "/api/auth/register", json=body)

    if response_data.status_code != 200:
        raise HTTPException(status_code=response_data.status_code)
    
    user_id = await session.execute(insert(Table_Users).values({
        Table_Users.login: user_data.email,
        Table_Users.fio: user_data.fio,
        Table_Users.password: user_data.password
    }).returning(Table_Users.id))
    
    user_id = str(user_id.mappings().first().id)
    await session.commit()
    
    
    response_data = response_data.json()
    response.headers.append("Authorization", f"Bearer {response_data["token"]}")
    
    redis = Redis(connection_pool=redis_connection_pool)
    redis.set(user_id, response_data["token"])
    
    response_data.update(
        id = user_id
    )
    return status_200(response_data)
    
    
@router.post("/login")
async def login(user_data: LoginSchema, response: Response, session: AsyncSession = Depends(get_session)):
    
    user_data.password = Security.encode_password(user_data.password)
    body = {
        "email": user_data.email,
        "password": user_data.password
    }

    response_data = await client.post(settings.API_ADDRESS + "/api/auth/login", json=body)
    
    if response_data.status_code != 200:
        raise HTTPException(status_code=response_data.status_code)
    
    user_id = await session.execute(select(Table_Users.id)
                              .where(Table_Users.login == user_data.email, Table_Users.password == user_data.password))
    user_id = str(user_id.mappings().first().id)
    
    response_data = response_data.json()
    redis = Redis(connection_pool=redis_connection_pool)
    
    redis.set(user_id, response_data["token"])
    response.headers.append("Authorization", f"Bearer {response_data["token"]}")
    
    response_data.update(
        id = user_id
    )
    return status_200(response_data)