from pydantic import BaseModel
from datetime import datetime


class STrainInfo(BaseModel):
    train_id: int
    startpoint: str
    startpoint_departure: datetime
    endpoint: str
    endpoint_arrival: datetime
    travel_time: int
    fullness: int
    suitable_wagons: list[int]
