from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from httpx import Headers
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete
from typing import Annotated

from app.utils import security, get_user_id_from_token
from app.db.configuration import get_session
from app.db.models import Order, OrderStatus
from app.schemas.orders import SOrderInfoNow, SOrderInfo, SOrderFavorite, SOrderAddInfo, SOrderSetStatus
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


@router.post("/favorite/add", status_code=status.HTTP_204_NO_CONTENT)
async def add_new_favorite(
    order_info: SOrderInfo,
    authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: AsyncSession = Depends(get_session)
) -> None:
    user_id = await get_user_id_from_token(authorization.credentials, session)
    query = update(Order).values(favorite=True).filter_by(
        user_id=user_id,
        train_id=order_info.train_id,
        wagon_id=order_info.wagon_id,
        seat_ids=order_info.seat_ids
    )
    try:
        await session.execute(query)
        await session.flush()
    except:
        print("bobo")


@router.post("/favorite/dell", status_code=status.HTTP_204_NO_CONTENT)
async def add_new_favorite(
    order_info: SOrderInfo,
    authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: AsyncSession = Depends(get_session)
) -> None:
    user_id = await get_user_id_from_token(authorization.credentials, session)
    query = update(Order).values(favorite=False).where(
        user_id=user_id,
        train_id=order_info.train_id,
        wagon_id=order_info.wagon_id,
        seat_ids=order_info.seat_ids
    )
    await session.execute(query)
    await session.commit()
    

@router.post("/buy", status_code=status.HTTP_204_NO_CONTENT)
async def buy_order(
        authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        order: SOrderAddInfo,
        session: AsyncSession = Depends(get_session)
) -> None:
    body = {
        "train_id": order.train_id,
        "wagon_id": order.wagon_id,
        "seat_ids": order.seat_ids
    }
    response = await client.post(
        url=f'{settings.API_ADDRESS}/api/order',
        json=body,
        headers=Headers({'Authorization': f'Bearer {authorization.credentials}'})
    )
    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=response.status_code)
    order_id = response.json()['order_id']

    user_id = await get_user_id_from_token(authorization.credentials, session)
    query = insert(Order).values(
        user_id=user_id,
        status=OrderStatus.BUY
        **order.model_dump()
    )
    await session.execute(query)
    await session.commit()
   
    
# @router.post("/wait", status_code=status.HTTP_204_NO_CONTENT)
# async def add_order(
#     authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)],
#         order: SOrderAddInfo,
#         session: AsyncSession = Depends(get_session)
# ) -> None:
    
#     user_id = await get_user_id_from_token(authorization.credentials, session)
#     query = insert(Order).values(
#         user_id = user_id,
#         status = OrderStatus.WAIT
#         **order.model_dump()
#     )
#     await session.execute(query)
#     await session.commit()
    
    
@router.post("/reserve", status_code=status.HTTP_204_NO_CONTENT)
async def add_order(
    authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        order: SOrderAddInfo,
        session: AsyncSession = Depends(get_session)
) -> None:
    
    user_id = await get_user_id_from_token(authorization.credentials, session)
    query = insert(Order).values(
        user_id = user_id,
        status = OrderStatus.RESERVE
        **order.model_dump()
    )
    await session.execute(query)
    await session.commit()


@router.put("/status", status_code=status.HTTP_204_NO_CONTENT)
async def update_status(
    authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        order: SOrderSetStatus,
        session: AsyncSession = Depends(get_session)
        
) -> None:
    user_id = await get_user_id_from_token(authorization.credentials, session)
    query = update(Order).values(
        status=order.status
    ).filter_by(
        train_id=order.train_id,
        wagon_id=order.wagon_id,
        seat_ids=order.seat_ids,
        user_id=user_id
    )
    await session.execute(query)
    await session.commit()
    
@router.delete("/del")
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
