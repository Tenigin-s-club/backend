from pydantic import BaseModel

class SAccountInfo(BaseModel):
    fio: str
    email: str
    
class SAccountOrders(BaseModel):
    train_id: int
    wagon_id: int
    seat_ids: int
    departure_date: str
    arriving_data: str
    start_point: str
    finish_point: str