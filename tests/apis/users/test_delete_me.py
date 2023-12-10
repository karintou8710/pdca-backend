import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.cruds import user as user_cruds
from tests.data import CREDENTIAL_ERROR_RESPONSE
from tests.types.common import SignUpUserInfo
from tests.types.response import ErrorResponse


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
