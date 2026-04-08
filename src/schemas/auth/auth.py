from pydantic import BaseModel

class LoginSchema(BaseModel):
    login: str
    password: str

class RegisterSchema(BaseModel):
    login: str
    password: str
