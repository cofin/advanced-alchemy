import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from advanced_alchemy.base import UUIDBase
from advanced_alchemy.extensions.starlette import AdvancedAlchemy, SQLAlchemyAsyncConfig
from advanced_alchemy.extensions.starlette.providers import provide_async_services
from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService


class StarletteUser(UUIDBase):
    pass


class StarletteUserService(SQLAlchemyAsyncRepositoryService[StarletteUser]):
    class Repo(SQLAlchemyAsyncRepository[StarletteUser]):
        model_type = StarletteUser

    repository_type = Repo


class StarletteTask(UUIDBase):
    pass


class StarletteTaskService(SQLAlchemyAsyncRepositoryService[StarletteTask]):
    class Repo(SQLAlchemyAsyncRepository[StarletteTask]):
        model_type = StarletteTask

    repository_type = Repo


@pytest.fixture
def config() -> SQLAlchemyAsyncConfig:
    return SQLAlchemyAsyncConfig(connection_string="sqlite+aiosqlite:///:memory:")


@pytest.fixture
def extension(config: SQLAlchemyAsyncConfig) -> AdvancedAlchemy:
    return AdvancedAlchemy(config=config)


async def test_provide_async_services_explicit_session(config: SQLAlchemyAsyncConfig) -> None:
    async with config.get_session() as session:
        async with provide_async_services(StarletteUserService, session=session, config=config) as (
            starlette_user_service,
        ):
            assert isinstance(starlette_user_service, StarletteUserService)
            assert starlette_user_service.repository.session is session


async def test_provide_async_services_standalone(config: SQLAlchemyAsyncConfig) -> None:
    async with provide_async_services(StarletteUserService, config=config) as (starlette_user_service,):
        assert isinstance(starlette_user_service, StarletteUserService)
        assert isinstance(starlette_user_service.repository.session, AsyncSession)


async def test_provide_async_services_request_scoped(config: SQLAlchemyAsyncConfig) -> None:
    app = Starlette()

    async def root(request: Request) -> JSONResponse:
        async with config.get_session() as session:
            setattr(request.state, config.session_key, session)
            async with provide_async_services(
                StarletteUserService, StarletteTaskService, request=request, config=config
            ) as (
                starlette_user_service,
                starlette_task_service,
            ):
                assert isinstance(starlette_user_service, StarletteUserService)
                assert isinstance(starlette_task_service, StarletteTaskService)
                assert starlette_user_service.repository.session is session
                assert starlette_task_service.repository.session is session
        return JSONResponse({"status": "ok"})

    app.router.routes.append(Route("/", endpoint=root))

    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200


async def test_provide_async_services_errors(config: SQLAlchemyAsyncConfig) -> None:
    # Both session and request
    async with config.get_session() as session:
        request = Request(scope={"type": "http"})
        with pytest.raises(ValueError, match="Cannot provide both 'session' and 'request'"):
            async with provide_async_services(StarletteUserService, session=session, request=request, config=config):
                pass

    # No inputs
    with pytest.raises(ValueError, match="At least one service provider or class is required"):
        async with provide_async_services(config=config):  # type: ignore
            pass

    # Request mode but no session in state
    request = Request(scope={"type": "http"})
    with pytest.raises(RuntimeError, match=r"ensure the extension's middleware is registered"):
        async with provide_async_services(StarletteUserService, request=request, config=config):
            pass
