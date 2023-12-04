from typing import TypedDict


class UserResponse(TypedDict):
    id: str
    name: str


class ErrorResponse(TypedDict):
    code: str
    message: str
