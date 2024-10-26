from pydantic import BaseModel

from app.db.models import OrderStatus


class SOrderBase:
    train_id: int
    wagon_id: int
    seat_ids: int 


class SOrderInfo(BaseModel, SOrderBase):
    pass


class SOrderInfoNow(BaseModel, SOrderBase):
    wait: bool

    
class SOrderAddInfo(BaseModel, SOrderBase):
    departure_date: str
    arriving_data: str
    start_point: str
    finish_point: str
    type_wagon: str
    type_shelf: str
    number_wagon: int
    number_seat: int
    stops: list[str]
    
    
class SOrderFavorite(BaseModel, SOrderBase):
    waite: bool
    favorite: bool
    
    
class SOrderSetStatus(BaseModel, SOrderBase):
    status: OrderStatus
    
    
