from fastapi import APIRouter, Depends, Query
from fastapi.security import HTTPAuthorizationCredentials

from app.config import client, settings, DATETIME_FORMAT
from app.utils import security
from app.schemas.search import STrainInfo
from httpx import Headers
from datetime import date, datetime
from typing import Annotated, Literal

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
        wagon_type: list[Literal['PLATZCART', 'COUPE']] = Query(),
        fullness_type: list[Literal['LOW', 'MEDIUM', 'HIGH']] = Query(),
        # время поездки в минутах
        min_travel_time: int | None = None,
        max_travel_time: int | None = None
) -> list[STrainInfo]:
    # получение поездов по нужному маршруту откуда-куда
    response = await client.get(
        url=f'{settings.API_ADDRESS}/api/info/trains',
        params=[('start_point', start_point), ('end_point', end_point)],
        headers=Headers({'Authorization': f'Bearer {authorization.credentials}'})
    )

    suitable_trains = []
    for train in response.json():
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
        if ((min_travel_time and train_travel_time < max_travel_time)
                or (max_travel_time and train_travel_time > max_travel_time)): continue

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


@router.get('/cities')
def get_cities_names() -> list[str]:
    with open('cities.txt', 'r') as file:
        cities = file.read().splitlines()
    return cities
