from typing import TypedDict


# user
class UpdateUserBody(TypedDict):
    name: str


class SignUpBody(TypedDict):
    name: str
    password: str


class LoginBody(TypedDict):
    name: str
    password: str


# task
class CreateTask(TypedDict):
    title: str
