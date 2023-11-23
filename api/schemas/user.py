from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str


class SignUpResponse(BaseModel):
    user: User
    access_token: str
    token_type: str


class LoginResponse(BaseModel):
    user: User
    access_token: str
    token_type: str


class UserUpdate(BaseModel):
    name: str


class Login(BaseModel):
    name: str
    password: str


class SignUp(BaseModel):
    name: str
    password: str
