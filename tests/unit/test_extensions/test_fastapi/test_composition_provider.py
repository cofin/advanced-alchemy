import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from advanced_alchemy.base import UUIDBase
from advanced_alchemy.extensions.fastapi import AdvancedAlchemy, SQLAlchemyAsyncConfig
from advanced_alchemy.extensions.fastapi.providers import provide_async_services
from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService


class FastAPIUser(UUIDBase):
    pass


class FastAPIUserService(SQLAlchemyAsyncRepositoryService[FastAPIUser]):
    class Repo(SQLAlchemyAsyncRepository[FastAPIUser]):
        model_type = FastAPIUser

    repository_type = Repo


class FastAPITask(UUIDBase):
    pass


class FastAPITaskService(SQLAlchemyAsyncRepositoryService[FastAPITask]):
    class Repo(SQLAlchemyAsyncRepository[FastAPITask]):
        model_type = FastAPITask

    repository_type = Repo


@pytest.fixture
def config() -> SQLAlchemyAsyncConfig:
    return SQLAlchemyAsyncConfig(connection_string="sqlite+aiosqlite:///:memory:")


@pytest.fixture
def extension(config: SQLAlchemyAsyncConfig) -> AdvancedAlchemy:
    return AdvancedAlchemy(config=config)


async def test_provide_async_services_explicit_session(config: SQLAlchemyAsyncConfig) -> None:
    async with config.get_session() as session:
        async with provide_async_services(FastAPIUserService, session=session, config=config) as (
            fastapi_user_service,
        ):
            assert isinstance(fastapi_user_service, FastAPIUserService)
            assert fastapi_user_service.repository.session is session


async def test_provide_async_services_standalone(config: SQLAlchemyAsyncConfig) -> None:
    async with provide_async_services(FastAPIUserService, config=config) as (fastapi_user_service,):
        assert isinstance(fastapi_user_service, FastAPIUserService)
        assert isinstance(fastapi_user_service.repository.session, AsyncSession)


async def test_provide_async_services_request_scoped(config: SQLAlchemyAsyncConfig) -> None:
    app = FastAPI()
    # Mocking what the middleware would do

    @app.get("/")
    async def root(request: Request) -> dict[str, str]:
        async with config.get_session() as session:
            setattr(request.state, config.session_key, session)
            async with provide_async_services(
                FastAPIUserService, FastAPITaskService, request=request, config=config
            ) as (
                fastapi_user_service,
                fastapi_task_service,
            ):
                assert isinstance(fastapi_user_service, FastAPIUserService)
                assert isinstance(fastapi_task_service, FastAPITaskService)
                assert fastapi_user_service.repository.session is session
                assert fastapi_task_service.repository.session is session
        return {"status": "ok"}

    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200


async def test_provide_async_services_errors(config: SQLAlchemyAsyncConfig) -> None:
    # Both session and request
    async with config.get_session() as session:
        request = Request(scope={"type": "http"})
        with pytest.raises(ValueError, match="Cannot provide both 'session' and 'request'"):
            async with provide_async_services(FastAPIUserService, session=session, request=request, config=config):
                pass

    # No inputs
    with pytest.raises(ValueError, match="At least one service provider or class is required"):
        async with provide_async_services(config=config):  # type: ignore
            pass

    # Request mode but no session in state
    request = Request(scope={"type": "http"})
    with pytest.raises(RuntimeError, match=r"ensure the.*middleware is registered"):
        async with provide_async_services(FastAPIUserService, request=request, config=config):
            pass
