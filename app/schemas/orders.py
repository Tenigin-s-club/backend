from pydantic import BaseModel


class SOrderInfo(BaseModel):
    wait: bool
    train_id: int
    wagon_id: int
    seat_ids: int


class SOrderAdd(BaseModel):
    train_id: int
    wagon_id: int
    seat_ids: int
