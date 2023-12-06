from datetime import timedelta

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.cruds import user as user_cruds
from api.oauth2 import create_access_token
from api.schemas import user as user_schema
from tests.data import (
    ALREADY_EXIST_ERROR_RESPONSE,
    CREDENTIAL_ERROR_RESPONSE,
    EXPIRED_SIGNATURE_ERROR_RESPONSE,
    LOGIN_VALIDATION_ERROR_RESPONSE,
    NOT_AUTHENTICATED_ERROR_RESPONSE,
    VALIDATION_ERROR_RESPONSE,
)
from tests.types.common import SignUpUserInfo
from tests.types.request import LoginBody, SignUpBody, UpdateUserBody
from tests.types.response import (
    ErrorResponse,
    LoginResponse,
    SignUpResponse,
    UserResponse,
)


class TestReadMe:
    @pytest.mark.asyncio
    async def test_read_me(
        self, async_client: AsyncClient, user_signup: SignUpUserInfo
    ) -> None:
        response = await async_client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {user_signup['accessToken']}"},
        )
        assert response.status_code == status.HTTP_200_OK

        data: UserResponse = response.json()
        EXPECT_RESPONSE: UserResponse = {
            "id": user_signup["user"]["id"],
            "name": "user1",
        }
        assert data == EXPECT_RESPONSE

    @pytest.mark.asyncio
    async def test_error_read_me_without_jwt(self, async_client: AsyncClient) -> None:
        response = await async_client.get(
            "/api/users/me",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data: ErrorResponse = response.json()
        assert data == NOT_AUTHENTICATED_ERROR_RESPONSE

    @pytest.mark.asyncio
    async def test_error_read_me_with_expired_jwt(
        self, async_client: AsyncClient, test_db: AsyncSession
    ) -> None:
        async with test_db.begin():
            sign_up_body = user_schema.SignUp(name="user1", password="password")
            user = await user_cruds.create_user(test_db, sign_up_body)
            jwtData = {"sub": user.id, "name": user.name}
            access_token = create_access_token(
                data=jwtData, expires_delta=timedelta(-1)
            )

        response = await async_client.get(
            "/api/users/me", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        data: ErrorResponse = response.json()
        assert data == EXPIRED_SIGNATURE_ERROR_RESPONSE


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


class TestDeleteMe:
    @pytest.mark.asyncio
    async def test_delete_me(
        self,
        async_client: AsyncClient,
        user_signup: SignUpUserInfo,
        test_db: AsyncSession,
    ) -> None:
        response = await async_client.delete(
            "/api/users/me",
            headers={"Authorization": f"Bearer {user_signup['accessToken']}"},
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        data: str = response.text
        assert data == ""

        async with test_db.begin():
            user_db = await user_cruds.fetch_user_by_id(
                test_db, user_signup["user"]["id"]
            )
            assert user_db is None

    @pytest.mark.asyncio
    async def test_error_delete_me_by_deleted_user(
        self,
        async_client: AsyncClient,
        user_signup: SignUpUserInfo,
        test_db: AsyncSession,
    ) -> None:
        # ユーザーの削除
        async with test_db.begin():
            await user_cruds.delete_user(test_db, user_signup["user"]["id"])

        response = await async_client.delete(
            "/api/users/me",
            headers={"Authorization": f"Bearer {user_signup['accessToken']}"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        data: ErrorResponse = response.json()
        assert data == CREDENTIAL_ERROR_RESPONSE


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
