from unittest.mock import MagicMock

import pytest
from sanic import HTTPResponse, Request, Sanic
from sanic.response import json
from sqlalchemy.ext.asyncio import AsyncSession

from advanced_alchemy.base import UUIDBase
from advanced_alchemy.extensions.sanic import AdvancedAlchemy, SQLAlchemyAsyncConfig
from advanced_alchemy.extensions.sanic.providers import provide_async_services
from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService


class SanicUser(UUIDBase):
    pass


class SanicUserService(SQLAlchemyAsyncRepositoryService[SanicUser]):
    class Repo(SQLAlchemyAsyncRepository[SanicUser]):
        model_type = SanicUser

    repository_type = Repo


class SanicTask(UUIDBase):
    pass


class SanicTaskService(SQLAlchemyAsyncRepositoryService[SanicTask]):
    class Repo(SQLAlchemyAsyncRepository[SanicTask]):
        model_type = SanicTask

    repository_type = Repo


@pytest.fixture
def config() -> SQLAlchemyAsyncConfig:
    return SQLAlchemyAsyncConfig(connection_string="sqlite+aiosqlite:///:memory:")


@pytest.fixture
def extension(config: SQLAlchemyAsyncConfig) -> AdvancedAlchemy:
    return AdvancedAlchemy(sqlalchemy_config=config)


async def test_provide_async_services_explicit_session(config: SQLAlchemyAsyncConfig) -> None:
    async with config.get_session() as session:
        async with provide_async_services(SanicUserService, session=session, config=config) as (sanic_user_service,):
            assert isinstance(sanic_user_service, SanicUserService)
            assert sanic_user_service.repository.session is session


async def test_provide_async_services_standalone(config: SQLAlchemyAsyncConfig) -> None:
    async with provide_async_services(SanicUserService, config=config) as (sanic_user_service,):
        assert isinstance(sanic_user_service, SanicUserService)
        assert isinstance(sanic_user_service.repository.session, AsyncSession)


async def test_provide_async_services_request_scoped(config: SQLAlchemyAsyncConfig) -> None:
    app = Sanic("TestApp")

    @app.get("/")  # type: ignore[misc]
    async def root(request: Request) -> HTTPResponse:
        async with config.get_session() as session:
            setattr(request.ctx, config.session_key, session)
            async with provide_async_services(SanicUserService, SanicTaskService, request=request, config=config) as (
                sanic_user_service,
                sanic_task_service,
            ):
                assert isinstance(sanic_user_service, SanicUserService)
                assert isinstance(sanic_task_service, SanicTaskService)
                assert sanic_user_service.repository.session is session
                assert sanic_task_service.repository.session is session
        return json({"status": "ok"})

    _, response = await app.asgi_client.get("/")
    assert response.status == 200


async def test_provide_async_services_errors(config: SQLAlchemyAsyncConfig) -> None:
    # Both session and request
    async with config.get_session() as session:
        request = MagicMock(spec=Request)
        with pytest.raises(ValueError, match="Cannot provide both 'session' and 'request'"):
            async with provide_async_services(SanicUserService, session=session, request=request, config=config):
                pass

    # No inputs
    with pytest.raises(ValueError, match="At least one service provider or class is required"):
        async with provide_async_services(config=config):  # type: ignore
            pass

    # Request mode but no session in state
    request = MagicMock(spec=Request)
    request.ctx = object()  # plain object has no session_key attribute
    with pytest.raises(RuntimeError, match=r"ensure the extension's middleware is registered"):
        async with provide_async_services(SanicUserService, request=request, config=config):
            pass
