import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.cruds import user as user_cruds
from tests.data import ALREADY_EXIST_ERROR_RESPONSE, VALIDATION_ERROR_RESPONSE
from tests.types.common import SignUpUserInfo
from tests.types.request import SignUpBody
from tests.types.response import ErrorResponse, SignUpResponse, UserResponse


class TestSignUp:
    @pytest.mark.asyncio
    async def test_signup(
        self, async_client: AsyncClient, test_db: AsyncSession
    ) -> None:
        body: SignUpBody = {"name": "user1", "password": "password"}
        response = await async_client.post("/api/signup", json=body)
        assert response.status_code == status.HTTP_201_CREATED

        data: SignUpResponse = response.json()
        EXPECT_USER: UserResponse = {"id": data["user"]["id"], "name": body["name"]}
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert data["user"] == EXPECT_USER

        # ユーザーの存在確認
        async with test_db.begin():
            user_db = await user_cruds.fetch_user_by_id(test_db, data["user"]["id"])
            assert user_db is not None

        # アクセストークンのテスト
        response = await async_client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {data['access_token']}"},
        )
        assert response.status_code == status.HTTP_200_OK

        data_me: UserResponse = response.json()
        assert data_me == EXPECT_USER

    @pytest.mark.asyncio
    async def test_error_signup_by_validation_error(
        self, async_client: AsyncClient
    ) -> None:
        body: SignUpBody = {"name": "user1", "password": ""}
        response = await async_client.post(
            "/api/signup",
            json=body,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        data: ErrorResponse = response.json()
        assert data == VALIDATION_ERROR_RESPONSE

    @pytest.mark.asyncio
    async def test_error_signup_by_existed_name(
        self, async_client: AsyncClient, user_signup: SignUpUserInfo
    ) -> None:
        body: SignUpBody = {"name": "user1", "password": "password"}
        response = await async_client.post(
            "/api/signup",
            json=body,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        data: ErrorResponse = response.json()
        assert data == ALREADY_EXIST_ERROR_RESPONSE
