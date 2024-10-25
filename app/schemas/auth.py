from pydantic import BaseModel

class RegisterSchema(BaseModel):
    fio: str
    email: str
    password: str
    team: str
    
class LoginSchema(BaseModel):
    email: str
    password: str