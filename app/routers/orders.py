from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from httpx import Headers
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete
from typing import Annotated

from app.utils import security, get_user_id_from_token, new_order
from app.db.configuration import get_session
from app.db.models import Order, OrderStatus
from app.schemas.orders import SOrderInfoNow, SOrderInfo, SOrderFavorite, SOrderAddInfo, SOrderSetStatus
from app.config import client, settings


router = APIRouter(
    prefix='/orders',
    tags=['orders']
)
 

@router.post("/buy", status_code=status.HTTP_204_NO_CONTENT)
async def buy_order(
        authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        order: SOrderAddInfo,
        session: AsyncSession = Depends(get_session)
) -> None:

    await new_order(SOrderInfo(**order.model_dump()), authorization.credentials)
    user_id = await get_user_id_from_token(authorization.credentials, session)
    query = insert(Order).values(
        user_id=user_id,
        status=OrderStatus.BUY.value,
        **order.model_dump()
    )
    await session.execute(query)
    await session.commit()
   
    
@router.post("/reserve", status_code=status.HTTP_204_NO_CONTENT)
async def reserve_order(
    authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        order: SOrderAddInfo,
        session: AsyncSession = Depends(get_session)
) -> None:
    
    user_id = await get_user_id_from_token(authorization.credentials, session)
    check_query = select(Order.id).filter_by(
        train_id=order.train_id,
        wagon_id=order.wagon_id,
        seat_ids=order.seat_ids
    )
    response_check = await session.execute(check_query)
    if response_check.scalar():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    
    query = insert(Order).values(
        user_id = user_id,
        status = OrderStatus.RESERVE.value,
        **order.model_dump()
    )
    await session.execute(query)
    await session.commit()


@router.put("/status/checkout", status_code=status.HTTP_204_NO_CONTENT)
async def update_status(
    authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        order: SOrderSetStatus,
        session: AsyncSession = Depends(get_session)
        
) -> None:
    await new_order(SOrderInfo(**order.model_dump()), authorization.credentials)
    user_id = await get_user_id_from_token(authorization.credentials, session)
    
    query = update(Order).values(
        status=OrderStatus.BUY.value
    ).filter_by(
        train_id=order.train_id,
        wagon_id=order.wagon_id,
        seat_ids=order.seat_ids,
        user_id=user_id
    )
    await session.execute(query)
    await session.commit()
    
@router.delete("/del", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        order: SOrderInfo,
        session: AsyncSession = Depends(get_session)
) -> None:
    user_id = await get_user_id_from_token(authorization.credentials, session)
    query = delete(Order).filter_by(
        user_id=user_id,
        train_id=order.train_id,
        wagon_id=order.wagon_id,
        seat_ids=order.seat_ids
    )
    await session.execute(query)
    await session.commit()
