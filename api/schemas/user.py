from pydantic import BaseModel, ConfigDict, Field


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
    name: str = Field(min_length=1)


class Login(BaseModel):
    name: str = Field(min_length=1)
    password: str = Field(min_length=1)


class SignUp(BaseModel):
    name: str = Field(min_length=1)
    password: str = Field(min_length=1)
