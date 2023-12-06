from typing import TypedDict


class UpdateUserBody(TypedDict):
    name: str


class SignUpBody(TypedDict):
    name: str
    password: str


class LoginBody(TypedDict):
    name: str
    password: str
