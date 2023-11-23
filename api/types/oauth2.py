from typing import TypedDict


class JwtUser(TypedDict):
    sub: str
    name: str
