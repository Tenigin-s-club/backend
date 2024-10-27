from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import insert

from app.config import DATETIME_FORMAT, redis_connection_pool
from app.db.configuration import get_session
from app.db.models import Wait
from app.utils import security, get_user_id_from_token
from app.schemas.search import STrainInfo
from datetime import date, datetime
from typing import Annotated, Literal
from redis import Redis
from uuid import uuid4
from json import loads, dumps

router = APIRouter(
    prefix='/search',
    tags=['search']
)
# уровни заполненности поезда по процентному отношению доступных мест к общему количеству
fullness_types = {
    'LOW': (0, 29),
    'MEDIUM': (30, 69),
    'HIGH': (70, 100),
}
# общее количество мест в вагоне по его типу
seats_in_wagon = {
    'PLATZCART': 54,
    'COUPE': 36
}


@router.get('')
async def search(
        authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        start_point: str,
        end_point: str,
        # дата в формате 2024-10-25
        departure_date: date,
        passenger_count: int,
        wagon_type: list[Literal['PLATZCART', 'COUPE']] = Query(),
        fullness_type: list[Literal['LOW', 'MEDIUM', 'HIGH']] = Query(),
        # время поездки в минутах
        min_travel_time: int | None = None,
        max_travel_time: int | None = None
) -> list[STrainInfo]:
    search_id = str(uuid4())
    # получение поездов по нужному маршруту откуда-куда
    redis = Redis(connection_pool=redis_connection_pool)
    redis.config_set('notify-keyspace-events', 'KEA')
    sub = redis.pubsub()
    sub.subscribe(f'__keyspace@0__:{search_id}')
    redis.lpush(
        'searchs',
        dumps({
            'type': 'base',
            'start_point': start_point,
            'end_point': end_point,
            'token': authorization.credentials,
            'search_id': search_id
        })
    )
    # отрегулировать timeout
    sub.get_message()
    message = sub.get_message(ignore_subscribe_messages=True, timeout=60.0)
    if not message:
        raise HTTPException(status_code=500, detail='external API don\'t answer to requests ;(')
    response = redis.get(search_id)
    redis.delete(search_id)

    suitable_trains = []
    for train in loads(response):
        startpoint_departure = datetime.strptime(train['startpoint_departure'], DATETIME_FORMAT)
        endpoint_arrival = datetime.strptime(train['endpoint_arrival'], DATETIME_FORMAT)
        train_travel_time = (endpoint_arrival - startpoint_departure).total_seconds() // 60
        total_seats_count = 0
        train_available_seats_count = train['available_seats_count']

        # на нужную ли дату этот поезд
        if departure_date != startpoint_departure.date(): continue
        # есть ли свободные места
        if train_available_seats_count == 0: continue
        # подходит ли под пользовательские рамки времени поездки
        if ((min_travel_time and train_travel_time < min_travel_time)
                or (max_travel_time and train_travel_time > max_travel_time)): continue
        # достаточно ли мест в вагоне
        if passenger_count > train_available_seats_count: continue

        redis.lpush(
            'searchs',
            dumps({
                'type': 'wagons',
                'train_id': train['train_id'],
                'token': authorization.credentials,
                'search_id': search_id
            })
        )
        sub.get_message()
        message = sub.get_message(ignore_subscribe_messages=True, timeout=60.0)
        if not message:
            raise HTTPException(status_code=500, detail='external API don\'t answer to requests ;(')
        response = redis.get(search_id)
        redis.delete(search_id)
        wagons = loads(response)

        suitable_wagons = []
        for wagon in train['wagons_info']:
            # подсчёт общего количества мест в поезде
            total_seats_count += seats_in_wagon[wagon['type']]
            # если вагон нужного пользователю типа - сохраняем его id
            if wagon['type'] not in wagon_type: continue
            suitable_wagons.append(wagon['wagon_id'])

        # наполненность поезда по показателю свободных мест в поезде / всего мест в поезде
        train_fullness = (1 - train_available_seats_count / total_seats_count) * 100
        # подходит ли под пользовательские рамки наполненность поезда
        if not (fullness_types[fullness_type][0] <= train_fullness <= fullness_types[fullness_type][1]): continue

        # поезд окончательно подходит пользователю, сохраняем его
        suitable_trains.append(STrainInfo(
            train_id=train['train_id'],
            startpoint=start_point,
            startpoint_departure=startpoint_departure,
            endpoint=end_point,
            endpoint_arrival=endpoint_arrival,
            travel_time=train_travel_time,
            fullness=train_fullness,
            suitable_wagons=suitable_wagons
        ))
    return suitable_trains


@router.post('/autobooking')
async def create_autobooking(
        authorization: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        train_id: int, session = Depends(get_session)
):
    user_id = get_user_id_from_token(authorization.credentials)
    query = insert(Wait).values(
        user_id=user_id,
        train_id=train_id
    )
    await session.execute(query)
    await session.commit()


@router.get('/cities')
def get_cities_names() -> list[str]:
    with open('cities.txt', 'r') as file:
        cities = file.read().splitlines()
    return cities
