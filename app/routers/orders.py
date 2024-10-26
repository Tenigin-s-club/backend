from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from redis import Redis

from app.db.configuration import get_session
from app.db.models import Table_Orders
from app.schemas.order import *
from app.config import client, settings, redis_connection_pool
from app.responses import *


router = APIRouter(
    prefix='/orders',
    tags=['orders']
)

    
@router.get("/all/{id}")
async def get_all_orders(id: int, session: AsyncSession = Depends(get_session)):
    pass

@router.post("/new")
async def add_new_order(order_data: AddSchema, session: AsyncSession = Depends(get_session)):
    redis = Redis
    body = {
        "train_id": order_data.train_id,
        "wagon_id": order_data.wagon_id,
        "seat_ids": order_data.seat_ids
    }
    headers = {
        "Authorization": ""
    }
    
    response_data = await client.post(settings.API_ADDRESS + "/api/order", json=body)
    
    if response_data.status_code != 200:
        raise HTTPException(status_code=response_data.status_code)
    
    response_data = response_data.json()
    
    await session.execute(insert(Table_Orders).values({
        Table_Orders.id: response_data["order_id"],
        Table_Orders.user: order_data.user_id,
        Table_Orders.train_id: order_data.train_id,
        Table_Orders.wagon_id: order_data.wagon_id,
        Table_Orders.seat_ids: order_data.seat_ids
    }))
    await session.commit()
    
    return status_200()