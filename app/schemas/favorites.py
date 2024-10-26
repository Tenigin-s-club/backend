from pydantic import BaseModel


class SBaseParams:
    train_id: int
    wagon_id: int
    seat_ids: int


class SExtParams(SBaseParams):
    departure_date: str
    arriving_data: str
    start_point: str
    finish_point: str
    type_wagon: str
    type_shelf: str
    number_wagon: int
    number_seat: int
    stops: list[str]
    

class SFavoritesAll(BaseModel, SExtParams):
    id: int

    
class SFavoritesAdd(BaseModel, SExtParams):
    pass