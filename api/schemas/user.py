from pydantic import BaseModel


class User(BaseModel):
    id: str
    name: str


class UserUpdate(BaseModel):
    name: str


class Login(BaseModel):
    name: str
    password: str


class SignUp(BaseModel):
    name: str
    password: str
