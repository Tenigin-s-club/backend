from pydantic import BaseModel


class SOrderInfoNow(BaseModel):
    wait: bool
    train_id: int
    wagon_id: int
    seat_ids: int


class SOrderInfo(BaseModel):
    train_id: int
    wagon_id: int
    seat_ids: int
    
class SOrderFavorite(BaseModel):
    waite: bool
    favorite: bool
    train_id: int
    wagon_id: int
    seat_ids: int
    
    
