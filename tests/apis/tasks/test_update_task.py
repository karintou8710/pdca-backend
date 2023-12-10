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
    VALIDATION_ERROR_RESPONSE,
)
from tests.types.common import SignUpUserInfo
from tests.types.request import CreateTask, UpdateTask
from tests.types.response import ErrorResponse, TaskResponse


class TestUpdateTask:
    @pytest.mark.asyncio
    async def test_update_task(
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

        body: UpdateTask = {"title": "Baseball"}
        response = await async_client.put(
            f"/api/tasks/{task_id}",
            json=body,
            headers={"Authorization": f"Bearer {user_signup['accessToken']}"},
        )
        assert response.status_code == status.HTTP_200_OK

        data: TaskResponse = response.json()
        EXPECT_RESPONSE: TaskResponse = {
            "id": data["id"],
            "title": body["title"],
            "user_id": user_signup["user"]["id"],
        }
        assert data == EXPECT_RESPONSE

        async with test_db.begin():
            res = await task_cruds.fetch_tasks_by_id(test_db, task_id)
            assert res is not None and res.title == body["title"]

    @pytest.mark.asyncio
    async def test_error_update_tasks_without_jwt(
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
        response = await async_client.put(
            f"/api/tasks/{task_id}",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data: ErrorResponse = response.json()
        assert data == NOT_AUTHENTICATED_ERROR_RESPONSE

    @pytest.mark.asyncio
    async def test_error_body_validation(
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

        body: CreateTask = {"title": ""}
        response = await async_client.put(
            f"/api/tasks/{task_id}",
            json=body,
            headers={"Authorization": f"Bearer {user_signup['accessToken']}"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        data: ErrorResponse = response.json()
        assert data == VALIDATION_ERROR_RESPONSE

    @pytest.mark.asyncio
    async def test_error_no_task(
        self,
        async_client: AsyncClient,
        user_signup: SignUpUserInfo,
    ) -> None:
        body: CreateTask = {"title": "notask"}
        response = await async_client.put(
            "/api/tasks/e3c114a3-48a9-48c3-9c9d-c50cbea02272",
            json=body,
            headers={"Authorization": f"Bearer {user_signup['accessToken']}"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

        data: ErrorResponse = response.json()
        assert data == NO_TASK_ERROR_RESPONSE

    @pytest.mark.asyncio
    async def test_error_update_other_user_task(
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

        # user2で更新する
        body: CreateTask = {"title": "Baseball"}
        response = await async_client.put(
            f"/api/tasks/{task_id}",
            json=body,
            headers={"Authorization": f"Bearer {user_signup2['accessToken']}"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        data: ErrorResponse = response.json()
        assert data == FORBIDDEN_ERROR_RESPONSE
