import pytest
from fastapi import status
from httpx import AsyncClient

from api.dependencies import get_current_user
from api.types.response import UserResponse
from main import app
from tests.data import USER1_RESPONSE


@pytest.mark.asyncio
async def test_read_me(async_client: AsyncClient) -> None:
    response = await async_client.get(
        "/api/users/me",
    )
    assert response.status_code == status.HTTP_200_OK
    data: UserResponse = response.json()
    assert data == USER1_RESPONSE


@pytest.mark.asyncio
async def test_read_me_without_jwt(async_client: AsyncClient) -> None:
    app.dependency_overrides[get_current_user] = get_current_user
    response = await async_client.get(
        "/api/users/me",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    # data = response.json()
