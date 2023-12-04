from typing import TypedDict


class UserInfo(TypedDict):
    id: str
    name: str
    password: str


class SignUpUserInfo(TypedDict):
    user: UserInfo
    accessToken: str
