import pytest
from fastapi import status
from httpx import AsyncClient

from tests.data import LOGIN_VALIDATION_ERROR_RESPONSE, VALIDATION_ERROR_RESPONSE
from tests.types.common import SignUpUserInfo
from tests.types.request import LoginBody
from tests.types.response import ErrorResponse, LoginResponse, UserResponse


class TestLogin:
    @pytest.mark.asyncio
    async def test_login(
        self, async_client: AsyncClient, user_signup: SignUpUserInfo
    ) -> None:
        body: LoginBody = {"name": "user1", "password": "password"}
        response = await async_client.post("/api/login", json=body)
        assert response.status_code == status.HTTP_200_OK

        data: LoginResponse = response.json()
        EXPECT_USER: UserResponse = {"id": data["user"]["id"], "name": body["name"]}
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert data["user"] == EXPECT_USER

        # アクセストークンのテスト
        response = await async_client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {data['access_token']}"},
        )
        assert response.status_code == status.HTTP_200_OK

        data_me: UserResponse = response.json()
        assert data_me == EXPECT_USER

    @pytest.mark.asyncio
    async def test_error_login_by_validation_error(
        self, async_client: AsyncClient, user_signup: SignUpUserInfo
    ) -> None:
        body: LoginBody = {"name": "user1", "password": ""}
        response = await async_client.post("/api/login", json=body)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        data: ErrorResponse = response.json()
        assert data == VALIDATION_ERROR_RESPONSE

    @pytest.mark.asyncio
    async def test_error_login_by_invalid_username(
        self, async_client: AsyncClient, user_signup: SignUpUserInfo
    ) -> None:
        body: LoginBody = {"name": "user2", "password": "password"}
        response = await async_client.post("/api/login", json=body)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        data: ErrorResponse = response.json()
        assert data == LOGIN_VALIDATION_ERROR_RESPONSE

    @pytest.mark.asyncio
    async def test_error_login_by_invalid_password(
        self, async_client: AsyncClient, user_signup: SignUpUserInfo
    ) -> None:
        body: LoginBody = {"name": "user1", "password": "invalid_password"}
        response = await async_client.post("/api/login", json=body)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        data: ErrorResponse = response.json()
        assert data == LOGIN_VALIDATION_ERROR_RESPONSE
