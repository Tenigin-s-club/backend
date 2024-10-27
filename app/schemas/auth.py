from pydantic import BaseModel, EmailStr


class SRegisterUser(BaseModel):
    fio: str
    email: str
    password: str

    
class SLoginUser(BaseModel):
    email: str
    password: str
