import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.cruds import user as user_cruds
from api.schemas import user as user_schema
from tests.data import (
    ALREADY_EXIST_ERROR_RESPONSE,
    CREDENTIAL_ERROR_RESPONSE,
    NOT_AUTHENTICATED_ERROR_RESPONSE,
    VALIDATION_ERROR_RESPONSE,
)
from tests.types.common import SignUpUserInfo
from tests.types.request import UpdateUserBody
from tests.types.response import ErrorResponse, UserResponse


class TestUpdateMe:
    @pytest.mark.asyncio
    async def test_update_me(
        self,
        async_client: AsyncClient,
        user_signup: SignUpUserInfo,
        test_db: AsyncSession,
    ) -> None:
        body: UpdateUserBody = {"name": "user1-updated"}
        response = await async_client.put(
            "/api/users/me",
            json=body,
            headers={"Authorization": f"Bearer {user_signup['accessToken']}"},
        )
        assert response.status_code == status.HTTP_200_OK

        data: UserResponse = response.json()
        EXPECT_RESPONSE: UserResponse = {
            "id": user_signup["user"]["id"],
            "name": body["name"],
        }
        assert data == EXPECT_RESPONSE

        async with test_db.begin():
            db_user = await user_cruds.fetch_user_by_id(test_db, data["id"])
            if db_user is None:
                raise Exception("no user")
            assert db_user.name == body["name"]

    @pytest.mark.asyncio
    async def test_error_update_me_without_jwt(self, async_client: AsyncClient) -> None:
        body: UpdateUserBody = {"name": "user1-updated"}
        response = await async_client.put("/api/users/me", json=body)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data: ErrorResponse = response.json()
        assert data == NOT_AUTHENTICATED_ERROR_RESPONSE

    @pytest.mark.asyncio
    async def test_error_update_me_to_existed_name(
        self,
        async_client: AsyncClient,
        user_signup: SignUpUserInfo,
        test_db: AsyncSession,
    ) -> None:
        # 新規ユーザーの作成
        async with test_db.begin():
            sign_up_body = user_schema.SignUp(name="new-user", password="password")
            await user_cruds.create_user(test_db, sign_up_body)

        body: UpdateUserBody = {"name": "new-user"}
        response = await async_client.put(
            "/api/users/me",
            json=body,
            headers={"Authorization": f"Bearer {user_signup['accessToken']}"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        data: ErrorResponse = response.json()
        assert data == ALREADY_EXIST_ERROR_RESPONSE

    @pytest.mark.asyncio
    async def test_error_update_me_by_deleted_user(
        self,
        async_client: AsyncClient,
        user_signup: SignUpUserInfo,
        test_db: AsyncSession,
    ) -> None:
        # ユーザーの削除
        async with test_db.begin():
            await user_cruds.delete_user(test_db, user_signup["user"]["id"])

        body: UpdateUserBody = {"name": "new-user"}
        response = await async_client.put(
            "/api/users/me",
            json=body,
            headers={"Authorization": f"Bearer {user_signup['accessToken']}"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        data: ErrorResponse = response.json()
        assert data == CREDENTIAL_ERROR_RESPONSE

    @pytest.mark.asyncio
    async def test_error_update_me_by_validation_error(
        self, async_client: AsyncClient, user_signup: SignUpUserInfo
    ) -> None:
        body: UpdateUserBody = {"name": ""}
        response = await async_client.put(
            "/api/users/me",
            json=body,
            headers={"Authorization": f"Bearer {user_signup['accessToken']}"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        data: ErrorResponse = response.json()
        assert data == VALIDATION_ERROR_RESPONSE
