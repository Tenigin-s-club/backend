from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated

from app.utils import security, get_user_id_from_token
from app.db.configuration import get_session
from app.db.models import Order, User
from app.schemas.account import SAccountInfo


router = APIRouter(
    prefix='/account',
    tags=['account']
)

@router.get("/info")
async def get_info_account(
        authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        session: AsyncSession = Depends(get_session)
) -> SAccountInfo:
    
    user_id = await get_user_id_from_token(authorization.credentials, session)
    query = select(User.fio).where(User.id == user_id)
    result = await session.execute(query)
    result = result.mappings().first()
    return SAccountInfo(**result)

@router.get("/orders")
async def get_orders(
        authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        session: AsyncSession = Depends(get_session)
):
    user_id = await get_user_id_from_token(authorization.credentials, session)
    pass

