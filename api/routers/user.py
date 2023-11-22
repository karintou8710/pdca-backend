from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.cruds import user as user_cruds
from api.db.db import get_db
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
async def sign_up(
    sign_up_body: user_schema.SignUp, db: AsyncSession = Depends(get_db)
) -> user_schema.User:
    async with db.begin():
        user = await user_cruds.create_user(db, sign_up_body)
        response = user_schema.User.model_validate(user)
    return response


@router.post("/login", response_model=user_schema.User)
async def login(login_body: user_schema.Login) -> user_schema.User:
    return user_schema.User(id="1", name="test_user")
