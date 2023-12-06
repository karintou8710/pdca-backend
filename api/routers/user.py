from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.cruds import user as user_cruds
from api.db.db import get_db
from api.dependencies import get_current_user
from api.errors import LoginValidationException, UserAlreadyExistException
from api.models.user import User as UserModel
from api.oauth2 import authenticate_user, create_access_token
from api.schemas import user as user_schema

router = APIRouter()


@router.get("/users/me", response_model=user_schema.User)
async def read_me(
    current_user: UserModel = Depends(get_current_user),
) -> user_schema.User:
    return user_schema.User.model_validate(current_user)


@router.put("/users/me", response_model=user_schema.User)
async def update_user(
    update_body: user_schema.UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> user_schema.User:
    user = await user_cruds.update_user(db, update_body, current_user.id)
    response = user_schema.User.model_validate(user)

    return response


@router.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
) -> None:
    await user_cruds.delete_user(db, current_user.id)


@router.post(
    "/signup",
    response_model=user_schema.SignUpResponse,
    status_code=status.HTTP_201_CREATED,
)
async def sign_up(
    sign_up_body: user_schema.SignUp, db: AsyncSession = Depends(get_db)
) -> user_schema.SignUpResponse:
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
