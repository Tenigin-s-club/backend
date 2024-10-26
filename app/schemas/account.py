from pydantic import BaseModel

class SAccountInfo(BaseModel):
    fio: str
    email: str