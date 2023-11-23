from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.cruds import user as user_cruds
from api.db.db import get_db
from api.errors import LoginValidationException, UserAlreadyExistException
from api.oauth2 import authenticate_user, create_access_token
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


@router.post("/signup", response_model=user_schema.SignUpResponse)
async def sign_up(
    sign_up_body: user_schema.SignUp, db: AsyncSession = Depends(get_db)
) -> user_schema.SignUpResponse:
    async with db.begin():
        created_user = await user_cruds.fetch_user_by_name(db, sign_up_body.name)
        if created_user is not None:
            raise UserAlreadyExistException()

        user = await user_cruds.create_user(db, sign_up_body)
        jwtData = {"sub": user.id, "name": user.name}
        access_token = create_access_token(data=jwtData)
        response = user_schema.SignUpResponse(
            user=user_schema.User.model_validate(user),
            access_token=access_token,
            token_type="bearer",
        )
    return response


@router.post("/login", response_model=user_schema.LoginResponse)
async def login(
    login_body: user_schema.Login, db: AsyncSession = Depends(get_db)
) -> user_schema.LoginResponse:
    async with db.begin():
        user = await authenticate_user(db, login_body.name, login_body.password)
        if user is None:
            raise LoginValidationException()
        jwtData = {"sub": user.id, "name": user.name}
        access_token = create_access_token(data=jwtData)
        response = user_schema.LoginResponse(
            user=user_schema.User.model_validate(user),
            access_token=access_token,
            token_type="bearer",
        )
    return response
