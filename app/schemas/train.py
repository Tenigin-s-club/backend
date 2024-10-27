from pydantic import BaseModel


class STrainObject(BaseModel):
    seatNum: str
    price: int
    bookingStatus: str = "CLOSED"

class STrainStorage(BaseModel):
    cupe: list[STrainObject]
    
    
class STrainWagonInfo(BaseModel):
    data: list[STrainStorage]
    
    
class STrainAllWagon(BaseModel):
    id: int
    wagon: list[STrainStorage]
    
class STrainAllTrain(BaseModel):
    train: list[STrainAllWagon]