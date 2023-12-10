import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.cruds import task as task_cruds
from api.schemas import task as task_schema
from tests.data import (
    FORBIDDEN_ERROR_RESPONSE,
    NOT_AUTHENTICATED_ERROR_RESPONSE,
    VALIDATION_ERROR_RESPONSE,
)
from tests.types.common import SignUpUserInfo
from tests.types.request import CreateTask, UpdateTask
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


class TestCreateTask:
    @pytest.mark.asyncio
    async def test_create_task(
        self,
        async_client: AsyncClient,
        user_signup: SignUpUserInfo,
        test_db: AsyncSession,
    ) -> None:
        body: CreateTask = {"title": "University Assignments"}
        response = await async_client.post(
            "/api/tasks",
            json=body,
            headers={"Authorization": f"Bearer {user_signup['accessToken']}"},
        )
        assert response.status_code == status.HTTP_201_CREATED

        data: TaskResponse = response.json()
        EXPECT_RESPONSE: TaskResponse = {
            "id": data["id"],
            "title": body["title"],
            "user_id": user_signup["user"]["id"],
        }
        assert data == EXPECT_RESPONSE

        async with test_db.begin():
            task = await task_cruds.fetch_tasks_by_id(test_db, data["id"])
            assert task is not None

    @pytest.mark.asyncio
    async def test_create_two_tasks(
        self,
        async_client: AsyncClient,
        user_signup: SignUpUserInfo,
        test_db: AsyncSession,
    ) -> None:
        body: CreateTask = {"title": "University Assignments"}
        body2: CreateTask = {"title": "Baseball"}

        # 1
        response1 = await async_client.post(
            "/api/tasks",
            json=body,
            headers={"Authorization": f"Bearer {user_signup['accessToken']}"},
        )
        assert response1.status_code == status.HTTP_201_CREATED

        data1: TaskResponse = response1.json()
        EXPECT_RESPONSE1: TaskResponse = {
            "id": data1["id"],
            "title": body["title"],
            "user_id": user_signup["user"]["id"],
        }
        assert data1 == EXPECT_RESPONSE1

        # 2
        response2 = await async_client.post(
            "/api/tasks",
            json=body2,
            headers={"Authorization": f"Bearer {user_signup['accessToken']}"},
        )
        assert response2.status_code == status.HTTP_201_CREATED

        data2: TaskResponse = response2.json()
        EXPECT_RESPONSE2: TaskResponse = {
            "id": data2["id"],
            "title": body2["title"],
            "user_id": user_signup["user"]["id"],
        }
        assert data2 == EXPECT_RESPONSE2

        async with test_db.begin():
            task1 = await task_cruds.fetch_tasks_by_id(test_db, data1["id"])
            task2 = await task_cruds.fetch_tasks_by_id(test_db, data2["id"])

            assert task1 is not None
            assert task2 is not None

    @pytest.mark.asyncio
    async def test_error_create_task_without_jwt(
        self,
        async_client: AsyncClient,
    ) -> None:
        response = await async_client.post(
            "/api/tasks",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data: ErrorResponse = response.json()
        assert data == NOT_AUTHENTICATED_ERROR_RESPONSE

    @pytest.mark.asyncio
    async def test_error_body_validation(
        self,
        async_client: AsyncClient,
        user_signup: SignUpUserInfo,
    ) -> None:
        body: CreateTask = {"title": ""}
        response = await async_client.post(
            "/api/tasks",
            json=body,
            headers={"Authorization": f"Bearer {user_signup['accessToken']}"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        data: ErrorResponse = response.json()
        assert data == VALIDATION_ERROR_RESPONSE


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
