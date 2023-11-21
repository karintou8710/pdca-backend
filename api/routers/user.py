from fastapi import APIRouter

from api.schemas import user as user_schema

router = APIRouter()


@router.get("/users/me", response_model=user_schema.User)
async def read_me() -> user_schema.User:
    return user_schema.User(id="1", name="test_user")


@router.put("/users/{user_id}", response_model=user_schema.User)
async def update_user(update_body: user_schema.UserUpdate) -> user_schema.User:
    return user_schema.User(id="1", name="test_user")


@router.delete("/users/{user_id}")
async def delete_user() -> None:
    pass


@router.post("/signup", response_model=user_schema.User)
async def sign_up(sign_up_body: user_schema.SignUp) -> user_schema.User:
    return user_schema.User(id="1", name="test_user")


@router.post("/login", response_model=user_schema.User)
async def login(login_body: user_schema.Login) -> user_schema.User:
    return user_schema.User(id="1", name="test_user")
