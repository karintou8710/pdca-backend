from typing import TypedDict


class UserResponse(TypedDict):
    id: str
    name: str


class SignUpResponse(TypedDict):
    user: UserResponse
    access_token: str
    token_type: str


class LoginResponse(TypedDict):
    user: UserResponse
    access_token: str
    token_type: str


class ErrorResponse(TypedDict):
    code: str
    message: str
