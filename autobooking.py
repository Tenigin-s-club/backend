import time
from random import randint

from redis import Redis
from sqlalchemy import select, delete, insert

from app.config import client, settings
from httpx import Headers
import asyncio
from json import loads, dumps

from app.db.configuration import redis_connection_pool, async_session_factory
from app.db.models import Order, Wait, User
from app.schemas.orders import SOrderInfo
from app.utils import new_order, send_mail

# очередь на redis
SEARCH_RPS = 3
WAITINGS_RPS = 6
TOTAL_RPS = SEARCH_RPS + WAITINGS_RPS

redis = Redis(connection_pool=redis_connection_pool)


async def process_waiting(waiting: dict):
    token = redis.get(str(waiting['user_id']))
    response = await client.get(
        url=f'{settings.API_ADDRESS}/api/info/wagons',
        params=[('train_id', waiting['train_id'])],
        headers=Headers({'Authorization': f'Bearer {token}'})
    )
    for wagon in response:
        for seat in wagon['seats']:
            if seat['bookingStatus'] == 'FREE':
                waiting['wagon_id'] = wagon['wagon_id']
                waiting['seat_ids'] = [seat['seat_id']]
                await new_order(SOrderInfo(
                    train_id=waiting['train_id'],
                    wagon_id=wagon['wagon_id'],
                    seat_ids=[seat['seat_id']]
                ), token)
    async with async_session_factory() as session:
        query = delete(Wait).filter_by(id=waiting['id'])
        await session.execute(query)
        await session.commit()

        response = await client.get(
            url=f'{settings.API_ADDRESS}/api/info/train/{waiting['train_id']}',
            headers=Headers({'Authorization': f'Bearer {token}'})
        )

        query = insert(Order).values(
            user_id=waiting['user_id'],
            status='RESERVE',
            train_id=waiting['train_id'],
            wagon_id=waiting['wagon_id'],
            seat_ids=waiting['seat_id'],
            departure_date=response['startpoint_departure'][:10],
            arriving_data=response['endpoint_arrival'][:10],
            start_point=response['detailed_route'][0]['name'],
            finish_point=response['detailed_route'][-1]['name']
        )
        await session.execute(query)
        await session.commit()

        query = select(User).filter_by(id=waiting['user_id'])
        result = await session.execute(query)
        user = result.mappings().one()

    send_mail(user['email'], user['fio'], response['startpoint_departure'][:10],
              response['detailed_route'][0]['name'], response['detailed_route'][-1]['name'])


async def process_search(search: bytes):
    decoded_search = loads(search.decode('utf-8').replace("'", '"'))
    match decoded_search['type']:
        case 'base':
            response = await client.get(
                url=f'{settings.API_ADDRESS}/api/info/trains',
                params=[('start_point', decoded_search['start_point']), ('end_point', decoded_search['end_point'])],
                headers=Headers({'Authorization': f'Bearer {decoded_search['token']}'})
            )
        case 'wagons':
            response = await client.get(
                url=f'{settings.API_ADDRESS}/api/info/wagons',
                params=[('train_id', decoded_search['train_id'])],
                headers=Headers({'Authorization': f'Bearer {decoded_search['token']}'})
            )
    redis.set(
        decoded_search['search_id'],
        dumps(response.json()) if response.status_code == 200 else 'something went wrong with external API :('
    )


async def get_waitings_list():
    # оптимизация получения из постгреса (ищем похожее, не шлём одинаковые запросы и т.п.)
    async with async_session_factory() as session:
        query = select(Wait.__table__.columns)
        result = await session.execute(query)
        return result.mappings().all()


async def runner():
    waitings_list = []
    while True:
        start_time = time.monotonic()
        if not waitings_list: waitings_list = await get_waitings_list()

        waitings_count = len(waitings_list)
        searchs_count = redis.llen('searchs')
        if (waitings_count >= WAITINGS_RPS) == (searchs_count >= SEARCH_RPS):
            waitings_count = min(waitings_count, WAITINGS_RPS)
            searchs_count = min(searchs_count, SEARCH_RPS)
        else:
            waitings_count = min(abs(TOTAL_RPS - searchs_count), waitings_count)
            searchs_count = min(abs(TOTAL_RPS - waitings_count), searchs_count)

        searches = redis.lpop('searchs', count=searchs_count) or []
        [asyncio.create_task(process_search(search)) for search in searches]
        [asyncio.create_task(process_waiting(waitings_list.pop())) for _ in range(waitings_count)]

        stop_time = time.monotonic()
        await asyncio.sleep(1 - (stop_time - start_time) if (stop_time - start_time > 1) else 0)


asyncio.run(runner())
