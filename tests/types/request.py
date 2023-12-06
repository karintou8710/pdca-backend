from typing import TypedDict


class UpdateUserBody(TypedDict):
    name: str


class SignUpBody(TypedDict):
    name: str
    password: str
