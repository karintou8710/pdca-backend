import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.cruds import task as task_cruds
from api.schemas import task as task_schema
from tests.data import (
    FORBIDDEN_ERROR_RESPONSE,
    NO_TASK_ERROR_RESPONSE,
    NOT_AUTHENTICATED_ERROR_RESPONSE,
)
from tests.types.common import SignUpUserInfo
from tests.types.response import ErrorResponse, TaskResponse


class TestGetTaskById:
    @pytest.mark.asyncio
    async def test_read_task(
        self,
        async_client: AsyncClient,
        user_signup: SignUpUserInfo,
        test_db: AsyncSession,
    ) -> None:
        # user1でタスクを作成する
        async with test_db.begin():
            param: task_schema.CreateTask = task_schema.CreateTask(
                title="University Assignments"
            )
            task = await task_cruds.create_task(
                test_db, user_signup["user"]["id"], param
            )
            task_id = task.id

        response = await async_client.get(
            f"/api/tasks/{task_id}",
            headers={"Authorization": f"Bearer {user_signup['accessToken']}"},
        )
        assert response.status_code == status.HTTP_200_OK

        data: TaskResponse = response.json()
        EXPECT_RESPONSE: TaskResponse = {
            "id": data["id"],
            "title": param.title,
            "user_id": user_signup["user"]["id"],
        }
        assert data == EXPECT_RESPONSE

    @pytest.mark.asyncio
    async def test_error_get_task_without_jwt(
        self,
        async_client: AsyncClient,
        user_signup: SignUpUserInfo,
        test_db: AsyncSession,
    ) -> None:
        # user1でタスクを作成する
        async with test_db.begin():
            param: task_schema.CreateTask = task_schema.CreateTask(
                title="University Assignments"
            )
            task = await task_cruds.create_task(
                test_db, user_signup["user"]["id"], param
            )
            task_id = task.id

        response = await async_client.get(
            f"/api/tasks/{task_id}",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data: ErrorResponse = response.json()
        assert data == NOT_AUTHENTICATED_ERROR_RESPONSE

    @pytest.mark.asyncio
    async def test_error_no_task(
        self,
        async_client: AsyncClient,
        user_signup: SignUpUserInfo,
    ) -> None:
        response = await async_client.get(
            "/api/tasks/e3c114a3-48a9-48c3-9c9d-c50cbea02272",
            headers={"Authorization": f"Bearer {user_signup['accessToken']}"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

        data: ErrorResponse = response.json()
        assert data == NO_TASK_ERROR_RESPONSE

    @pytest.mark.asyncio
    async def test_error_get_other_user_task(
        self,
        async_client: AsyncClient,
        user_signup: SignUpUserInfo,
        user_signup2: SignUpUserInfo,
        test_db: AsyncSession,
    ) -> None:
        # user1でタスクを作成する
        async with test_db.begin():
            param: task_schema.CreateTask = task_schema.CreateTask(
                title="University Assignments"
            )
            task = await task_cruds.create_task(
                test_db, user_signup["user"]["id"], param
            )
            task_id = task.id

        # user2で削除する
        response = await async_client.get(
            f"/api/tasks/{task_id}",
            headers={"Authorization": f"Bearer {user_signup2['accessToken']}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        data: ErrorResponse = response.json()
        assert data == FORBIDDEN_ERROR_RESPONSE