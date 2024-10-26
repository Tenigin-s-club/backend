from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from httpx import Headers
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update
from typing import Annotated

from app.utils import security, get_user_id_from_token
from app.db.configuration import get_session
from app.db.models.orders import Order
from app.schemas.orders import SOrderInfoNow, SOrderInfo, SOrderFavorite
from app.config import client, settings


router = APIRouter(
    prefix='/orders',
    tags=['orders']
)

    
@router.get('/', status_code=status.HTTP_200_OK)
async def get_orders(
        authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        session: AsyncSession = Depends(get_session)
) -> list[SOrderInfoNow]:
    user_id = await get_user_id_from_token(authorization.credentials, session)
    query = select(Order.__table__.columns).filter_by(user_id=user_id)
    result = await session.execute(query)
    orders = result.mappings().all()
    return [SOrderInfoNow(**order) for order in orders]


@router.get("/favorite/all")
async def get_favorite(
    authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: AsyncSession = Depends(get_session)
) -> list[SOrderFavorite]:
    user_id = await get_user_id_from_token(authorization.credentials, session)
    query = select(Order.__table__.columns).filter_by(favorite=True, user_id=user_id)
    result = await session.execute(query)
    orders = result.mappings().all()
    return [SOrderFavorite(**order) for order in orders]

@router.post("/favorite/add")
async def add_new_favorite(
    order_info: SOrderInfo,
    authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: AsyncSession = Depends(get_session)
) -> None:
    user_id = await get_user_id_from_token(authorization.credentials, session)
    query = update(Order).values(favorite=True).where(
        user_id=user_id,
        train_id=order_info.train_id,
        wagon_id=order_info.wagon_id,
        seat_ids=order_info.seat_ids
    )
    await session.execute(query)
    await session.commit()

@router.post("/", status_code=status.HTTP_204_NO_CONTENT)
async def add_new_order(
        authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        order: SOrderInfo,
        session: AsyncSession = Depends(get_session)
) -> None:
    response = await client.post(
        url=f'{settings.API_ADDRESS}/api/order',
        json=order.model_dump(),
        headers=Headers({'Authorization': f'Bearer {authorization.credentials}'})
    )
    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=response.status_code)
    order_id = response.json()['order_id']

    user_id = await get_user_id_from_token(authorization.credentials, session)
    query = insert(Order).values(
        id=order_id,
        user_id=user_id,
        **order.model_dump()
    )
    await session.execute(query)
    await session.commit()

