import json
import time
from datetime import date, datetime
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
# TOTAL_RPS = SEARCH_RPS + WAITINGS_RPS

redis = Redis(connection_pool=redis_connection_pool)


async def process_waiting(waiting: dict):
    token = redis.get(str(waiting['user_id']))
    response = await client.get(
        url=f'{settings.API_ADDRESS}/api/info/wagons',
        params=[('train_id', waiting['train_id'])],
        headers=Headers({'Authorization': f'Bearer {settings.TEAM_TOKEN}'})
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
                ))
    async with async_session_factory() as session:
        query = delete(Wait).filter_by(id=waiting['id'])
        await session.execute(query)
        await session.commit()

        response = await client.get(
            url=f'{settings.API_ADDRESS}/api/info/train/{waiting['train_id']}',
            headers=Headers({'Authorization': f'Bearer {settings.TEAM_TOKEN}'})
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
                headers=Headers({'Authorization': f'Bearer {settings.TEAM_TOKEN}'})
            )
        case 'wagons':
            response = await client.get(
                url=f'{settings.API_ADDRESS}/api/info/wagons',
                params=[('train_id', decoded_search['train_id'])],
                headers=Headers({'Authorization': f'Bearer {settings.TEAM_TOKEN}'})
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


async def book_train(user_wish):
    global data, new_data
    trains = await client.get(
        url=f'{settings.API_ADDRESS}/api/info/trains',
        params=[('start_point', user_wish['startpoint']), ('end_point', user_wish['endpoint'])],
        headers=Headers({'Authorization': f'Bearer {settings.TEAM_TOKEN}'})
    )
    train_id, wagon_id, seat_ids = None, None, []
    print(trains.status_code)
    if not trains or trains.status_code != 200:
        new_data.append(user_wish)
        return
    for train in trains.json():
        # на нужную ли дату этот поезд
        startpoint_departure = datetime.strptime(train['startpoint_departure'], '%d.%m.%Y %H:%M:%S')
        departure_dates = [datetime.strptime(dep, '%d.%m.%Y') for dep in user_wish['departure_dates']]
        if startpoint_departure not in departure_dates: continue
        # есть ли столько свободных мест на поезде
        if user_wish['ticket_count'] > train['available_seats_count']: continue
        # смотрим все вагоны поезда
        wagons = await client.get(
            url=f'{settings.API_ADDRESS}/api/info/wagons',
            params=[('train_id', train['train_id'])],
            headers=Headers({'Authorization': f'Bearer {settings.TEAM_TOKEN}'})
        )
        for wagon in wagons.json():
            # нужного ли типа этот вагон
            if wagon['type'] != user_wish['wagon_type']: continue
            need_lower, need_upper = user_wish['seat_preference'].count('lower'), user_wish['seat_preference'].count('upper')
            lower_passengers, upper_passengers = [], []
            for seat in wagon['seats']:
                # если место занято - пропускаем его
                if seat['bookingStatus'] != 'FREE': continue
                if seat['seatNum'] % 2: lower_passengers.append(seat['seat_id'])
                else: upper_passengers.append(seat['seat_id'])
            # хватит ли нужных (верхних/нижних) мест в поезде
            if need_lower > len(lower_passengers) or need_upper > len(upper_passengers): continue

            # прошли все критерии, значит вагон подходит к нам
            train_id = train['train_id']
            wagon_id = wagon['wagon_id']
            seat_ids = lower_passengers[:need_lower] + upper_passengers[:need_upper]

    # прошли все поезда, если не нашли подходящий поезд, то завершаемся
    if not train_id or not wagon_id or not seat_ids:
        new_data.append(user_wish)
        return
    # иначе бронируем место
    response = await client.post(
        url=f'{settings.API_ADDRESS}/api/order',
        json={
            'train_id': train_id,
            'wagon_id': wagon_id,
            'seat_ids': seat_ids
        },
        headers=Headers({'Authorization': f'Bearer {settings.TEAM_TOKEN}'})
    )
    if response.status_code == 200:
        print(f'{user_wish['id']}. wow')


async def runnerv2():
    await asyncio.sleep(5)
    while True:
        global data, new_data
        if not data:
            data = new_data.copy()
            new_data = []
        start_time = time.monotonic()
        for _ in range(TOTAL_RPS):
            _ = asyncio.create_task(book_train(data.pop()))
            await asyncio.sleep(sleep_time)
        stop_time = time.monotonic()
        await asyncio.sleep(1 - (stop_time - start_time) if (stop_time - start_time > 1) else 0)
        print('second end')


data = json.load(open('travel_data.json'))
new_data = []
TOTAL_RPS = 5
sleep_time = 0.9 / TOTAL_RPS
# asyncio.run(runner())
asyncio.run(runnerv2())
