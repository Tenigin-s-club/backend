from fastapi import APIRouter, Depends, Response
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert

from app.schemas.auth import *
from app.db.configuration import get_session
from app.config import client, settings
from app.db.models import Table_Users
from app.responses import status_200


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post("/register")
async def register(user_data: RegisterSchema, response: Response, session: AsyncSession = Depends(get_session)):
    body = { 
        "fio": user_data.fio,
        "email": user_data.email,
        "password": user_data.password,
        "team": user_data.team
}
    response_data = await client.post(settings.API_ADDRESS + "/api/auth/register", json=body)

    if response_data.status_code != 200:
        raise HTTPException(status_code=response_data.status_code)
    
    await session.execute(insert(Table_Users).values({
        Table_Users.login: user_data.email,
        Table_Users.fio: user_data.fio
    }))
    await session.commit()
    
    response_data = response_data.json()
    response.headers.append("Authorization", f"Bearer {response_data["token"]}")
    return status_200(response_data)
    
@router.post("/login")
async def login(user_data: LoginSchema, response: Response):
    body = {
        "email": user_data.email,
        "password": user_data.password
    }
    response_data = await client.post(settings.API_ADDRESS + "/api/auth/login", json=body)
    
    if response_data.status_code != 200:
        raise HTTPException(status_code=response_data.status_code)
    
    response_data = response_data.json()
    response.headers.append("Authorization", f"Bearer {response_data["token"]}")
    return status_200(response_data)