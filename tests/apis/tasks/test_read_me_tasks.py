import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.cruds import task as task_cruds
from api.schemas import task as task_schema
from tests.data import NOT_AUTHENTICATED_ERROR_RESPONSE
from tests.types.common import SignUpUserInfo
from tests.types.response import ErrorResponse, TaskResponse


class TestReadMeTasks:
    @pytest.mark.asyncio
    async def test_read_my_no_task(
        self, async_client: AsyncClient, user_signup: SignUpUserInfo
    ) -> None:
        response = await async_client.get(
            "/api/users/me/tasks",
            headers={"Authorization": f"Bearer {user_signup['accessToken']}"},
        )
        assert response.status_code == status.HTTP_200_OK

        data: list[TaskResponse] = response.json()
        EXPECT_RESPONSE: list[TaskResponse] = []
        assert data == EXPECT_RESPONSE

    @pytest.mark.asyncio
    async def test_read_my_one_task(
        self,
        async_client: AsyncClient,
        user_signup: SignUpUserInfo,
        test_db: AsyncSession,
    ) -> None:
        # タスクを作成する
        async with test_db.begin():
            param: task_schema.CreateTask = task_schema.CreateTask(
                title="University Assignments"
            )
            await task_cruds.create_task(test_db, user_signup["user"]["id"], param)

        response = await async_client.get(
            "/api/users/me/tasks",
            headers={"Authorization": f"Bearer {user_signup['accessToken']}"},
        )
        assert response.status_code == status.HTTP_200_OK

        data: list[TaskResponse] = response.json()
        EXPECT_RESPONSE: list[TaskResponse] = [
            {
                "id": data[0]["id"],
                "title": param.title,
                "user_id": user_signup["user"]["id"],
            }
        ]
        assert data == EXPECT_RESPONSE

    @pytest.mark.asyncio
    async def test_read_task_of_others(
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
            await task_cruds.create_task(test_db, user_signup["user"]["id"], param)

        # user2で取得する
        response = await async_client.get(
            "/api/users/me/tasks",
            headers={"Authorization": f"Bearer {user_signup2['accessToken']}"},
        )
        assert response.status_code == status.HTTP_200_OK

        data: list[TaskResponse] = response.json()
        EXPECT_RESPONSE: list[TaskResponse] = []
        assert data == EXPECT_RESPONSE

    @pytest.mark.asyncio
    async def test_error_read_tasks_without_jwt(
        self,
        async_client: AsyncClient,
    ) -> None:
        response = await async_client.get(
            "/api/users/me/tasks",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data: ErrorResponse = response.json()
        assert data == NOT_AUTHENTICATED_ERROR_RESPONSE
