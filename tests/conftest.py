# flake8: noqa
import os

from dotenv import load_dotenv

# settings.pyが読み込まれる前に、.envとTESTINGの設定をする
load_dotenv(verbose=True)

from typing import AsyncGenerator, Generator
from urllib.parse import urlparse

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy_utils import create_database, database_exists, drop_database

from api.cruds import user as user_cruds
from api.db.db import get_db
from api.db.migrate_base import Base
from api.oauth2 import create_access_token
from api.schemas import user as user_schema
from main import app
from tests.types.common import SignUpUserInfo

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "")
if TEST_DATABASE_URL == "":
    raise Exception("Please set TEST_DATABASE_URL as an environment variable")
TEST_DATABASE_SYNC_URL = (
    urlparse(TEST_DATABASE_URL)._replace(scheme="postgresql").geturl()
)

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
sessionLocal = async_sessionmaker(autocommit=False, autoflush=True, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def init_detabase() -> Generator[None, None, None]:
    # データベースの初期化
    if database_exists(TEST_DATABASE_SYNC_URL):
        drop_database(TEST_DATABASE_SYNC_URL)
    create_database(TEST_DATABASE_SYNC_URL)

    yield

    drop_database(TEST_DATABASE_SYNC_URL)


@pytest_asyncio.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    # テーブル作り直し
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async def test_db_with_transaction() -> AsyncGenerator[AsyncSession, None]:
        async with sessionLocal() as session:
            async with session.begin():
                yield session

    app.dependency_overrides[get_db] = test_db_with_transaction

    async with AsyncClient(app=app, base_url="http://localhost:3000") as client:
        yield client

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    async with sessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def user_signup(test_db: AsyncSession) -> AsyncGenerator[SignUpUserInfo, None]:
    async with test_db.begin():
        sign_up_body = user_schema.SignUp(name="user1", password="password")
        user = await user_cruds.create_user(test_db, sign_up_body)
        user_id = user.id
        jwtData = {"sub": user_id, "name": user.name}
        access_token = create_access_token(data=jwtData)
        userInfo: SignUpUserInfo = {
            "user": {"id": user.id, "name": user.name, "password": user.password},
            "accessToken": access_token,
        }

    yield userInfo
