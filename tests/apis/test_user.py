from datetime import timedelta

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.cruds import user as user_cruds
from api.oauth2 import create_access_token
from api.schemas import user as user_schema
from tests.data import (
    EXPIRED_SIGNATURE_ERROR_RESPONSE,
    NOT_AUTHENTICATED_ERROR_RESPONSE,
)
from tests.types.common import SignUpUserInfo
from tests.types.response import ErrorResponse, UserResponse


@pytest.mark.asyncio
async def test_read_me(async_client: AsyncClient, user_signup: SignUpUserInfo) -> None:
    response = await async_client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {user_signup['accessToken']}"},
    )
    assert response.status_code == status.HTTP_200_OK

    data: UserResponse = response.json()
    EXPECT_RESPONSE: UserResponse = {"id": user_signup["user"]["id"], "name": "user1"}
    assert data == EXPECT_RESPONSE


@pytest.mark.asyncio
async def test_error_read_me_without_jwt(async_client: AsyncClient) -> None:
    response = await async_client.get(
        "/api/users/me",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data: ErrorResponse = response.json()
    assert data == NOT_AUTHENTICATED_ERROR_RESPONSE


@pytest.mark.asyncio
async def test_error_read_me_with_expired_jwt(
    async_client: AsyncClient, test_db: AsyncSession
) -> None:
    async with test_db.begin():
        sign_up_body = user_schema.SignUp(name="user1", password="password")
        user = await user_cruds.create_user(test_db, sign_up_body)
        jwtData = {"sub": user.id, "name": user.name}
        access_token = create_access_token(data=jwtData, expires_delta=timedelta(-1))

    response = await async_client.get(
        "/api/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    data: ErrorResponse = response.json()
    assert data == EXPIRED_SIGNATURE_ERROR_RESPONSE
