from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Mapped, Session

from advanced_alchemy.base import UUIDBase
from advanced_alchemy.repository import (
    SQLAlchemyAsyncRepository,
    SQLAlchemyAsyncSlugRepository,
    SQLAlchemySyncRepository,
    SQLAlchemySyncSlugRepository,
)
from advanced_alchemy.service import (
    AsyncAutoSlugServiceMixin,
    AsyncCompositeServiceMixin,
    SQLAlchemyAsyncRepositoryService,
    SQLAlchemySyncRepositoryService,
    SyncAutoSlugServiceMixin,
    SyncCompositeServiceMixin,
)


class MockModel(UUIDBase):
    slug: Mapped[str]


class ChildAsyncService(SQLAlchemyAsyncRepositoryService[MockModel]):
    class Repo(SQLAlchemyAsyncRepository[MockModel]):
        model_type = MockModel

    repository_type = Repo


class ParentAsyncService(AsyncCompositeServiceMixin, SQLAlchemyAsyncRepositoryService[MockModel]):
    class Repo(SQLAlchemyAsyncRepository[MockModel]):
        model_type = MockModel

    repository_type = Repo

    @property
    def child(self) -> ChildAsyncService:
        return self._get_service(ChildAsyncService)


class ChildSyncService(SQLAlchemySyncRepositoryService[MockModel]):
    class Repo(SQLAlchemySyncRepository[MockModel]):
        model_type = MockModel

    repository_type = Repo


class ParentSyncService(SyncCompositeServiceMixin, SQLAlchemySyncRepositoryService[MockModel]):
    class Repo(SQLAlchemySyncRepository[MockModel]):
        model_type = MockModel

    repository_type = Repo

    @property
    def child(self) -> ChildSyncService:
        return self._get_service(ChildSyncService)


async def test_composite_async_service_mixin() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(UUIDBase.metadata.create_all)

    async with AsyncSession(engine) as session:
        service = ParentAsyncService(session=session)
        child = service.child

        assert isinstance(child, ChildAsyncService)
        assert child.repository.session is session
        # Test caching
        assert service.child is child


def test_composite_sync_service_mixin() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    UUIDBase.metadata.create_all(engine)

    with Session(engine) as session:
        service = ParentSyncService(session=session)
        child = service.child

        assert isinstance(child, ChildSyncService)
        assert child.repository.session is session
        # Test caching
        assert service.child is child


async def test_auto_slug_async_service_mixin() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(UUIDBase.metadata.create_all)

    async with AsyncSession(engine) as session:

        class AsyncSlugService(AsyncAutoSlugServiceMixin[MockModel], SQLAlchemyAsyncRepositoryService[MockModel]):
            class Repo(SQLAlchemyAsyncSlugRepository[MockModel]):
                model_type = MockModel

            repository_type = Repo

        service = AsyncSlugService(session=session)
        data = {"id": "00000000-0000-0000-0000-000000000001"}  # no slug

        # Mocking repository.get_available_slug
        # In a real app, this would be an async call
        async def mock_get_available_slug(value: str, **kwargs: Any) -> str:
            return "test-slug"

        service.repository.get_available_slug = mock_get_available_slug  # type: ignore

        instance = await service.to_model_on_create(data)
        assert isinstance(instance, dict)
        assert instance["slug"] == "test-slug"


def test_auto_slug_sync_service_mixin() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    UUIDBase.metadata.create_all(engine)

    with Session(engine) as session:

        class SyncSlugService(SyncAutoSlugServiceMixin[MockModel], SQLAlchemySyncRepositoryService[MockModel]):
            class Repo(SQLAlchemySyncSlugRepository[MockModel]):
                model_type = MockModel

            repository_type = Repo

        service = SyncSlugService(session=session)
        data = {"id": "00000000-0000-0000-0000-000000000001"}  # no slug

        # Mocking repository.get_available_slug
        def mock_get_available_slug(value: str, **kwargs: Any) -> str:
            return "test-slug-sync"

        service.repository.get_available_slug = mock_get_available_slug  # type: ignore

        instance = service.to_model_on_create(data)
        assert isinstance(instance, dict)
        assert instance["slug"] == "test-slug-sync"
