"""Tests for service composition primitives."""

from collections.abc import AsyncGenerator, AsyncIterator, Generator
from contextlib import asynccontextmanager
from typing import Any, cast
from unittest.mock import MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from advanced_alchemy.service import (
    ServiceWithSession,
    SQLAlchemyAsyncServiceComposition,
    SQLAlchemyAsyncServiceProvider,
    SQLAlchemySyncServiceComposition,
    compose_async_services,
    compose_sync_services,
    provide_async_services,
    provide_sync_services,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_async_session() -> MagicMock:
    return MagicMock(spec=AsyncSession)


@pytest.fixture
def mock_sync_session() -> MagicMock:
    return MagicMock(spec=Session)


class FakeServiceA:
    def __init__(self, *, session: AsyncSession) -> None:
        self.session = session


class FakeServiceB:
    def __init__(self, *, session: AsyncSession) -> None:
        self.session = session


class FakeServiceC:
    def __init__(self, *, session: AsyncSession) -> None:
        self.session = session


class FakeServiceWithNew:
    def __init__(self, *, session: AsyncSession) -> None:
        self.session = session
        self.entered = False
        self.exited = False

    @classmethod
    @asynccontextmanager
    async def new(cls, *, session: AsyncSession) -> AsyncIterator["FakeServiceWithNew"]:
        service = cls(session=session)
        service.entered = True
        try:
            yield service
        finally:
            service.exited = True


async def provider_a(session: AsyncSession) -> AsyncGenerator[FakeServiceA, None]:
    yield FakeServiceA(session=session)


async def provider_b(session: AsyncSession) -> AsyncGenerator[FakeServiceB, None]:
    yield FakeServiceB(session=session)


async def provider_c(session: AsyncSession) -> AsyncGenerator[FakeServiceC, None]:
    yield FakeServiceC(session=session)


def test_service_provider_alias_accepts_async_generator_provider() -> None:
    provider: SQLAlchemyAsyncServiceProvider[FakeServiceA] = provider_a

    assert provider is provider_a


@pytest.mark.asyncio
async def test_compose_async_services_returns_typed_composition() -> None:
    session = MagicMock(spec=AsyncSession)
    composer = compose_async_services(provider_a)

    async with composer.open(session=session) as services:
        (a,) = services

    assert isinstance(a, FakeServiceA)
    assert a.session is session


@pytest.mark.asyncio
async def test_chain_three_providers_share_session() -> None:
    session = MagicMock(spec=AsyncSession)
    composer = compose_async_services(provider_a).add(provider_b).add(provider_c)

    async with composer.open(session=session) as services:
        a, b, c = services

    assert isinstance(a, FakeServiceA)
    assert isinstance(b, FakeServiceB)
    assert isinstance(c, FakeServiceC)
    assert a.session is b.session is c.session is session


@pytest.mark.asyncio
async def test_class_injection_auto_instantiates() -> None:
    session = MagicMock(spec=AsyncSession)
    composer = compose_async_services(FakeServiceA).add(FakeServiceB)

    async with composer.open(session=session) as (a, b):
        assert isinstance(a, FakeServiceA)
        assert isinstance(b, FakeServiceB)
        assert a.session is b.session is session


@pytest.mark.asyncio
async def test_class_injection_with_new_hook() -> None:
    session = MagicMock(spec=AsyncSession)
    composer = compose_async_services(FakeServiceWithNew)

    async with composer.open(session=session) as (service,):
        assert isinstance(service, FakeServiceWithNew)
        assert service.session is session
        assert service.entered is True
        assert service.exited is False

    assert service.exited is True


@pytest.mark.asyncio
async def test_provide_async_services_shorthand() -> None:
    session = MagicMock(spec=AsyncSession)
    async with provide_async_services(provider_a, FakeServiceB, session=cast("Any", session)) as (a, b):  # type: ignore[call-overload]
        assert isinstance(a, FakeServiceA)
        assert isinstance(b, FakeServiceB)
        assert a.session is session


@pytest.mark.asyncio
async def test_provide_async_services_empty_raises() -> None:
    session = MagicMock(spec=AsyncSession)
    with pytest.raises(ValueError, match="At least one service"):
        async with provide_async_services(session=cast("Any", session)):  # type: ignore[call-overload]
            pass


@pytest.mark.asyncio
async def test_partial_failure_closes_entered_providers() -> None:
    cleanup_ran = False

    async def cleanup_provider(session: AsyncSession) -> AsyncGenerator[FakeServiceA, None]:
        try:
            yield FakeServiceA(session=session)
        finally:
            nonlocal cleanup_ran
            cleanup_ran = True

    async def failing_provider(session: AsyncSession) -> AsyncGenerator[Any, None]:
        if repr(session) == "unused":
            yield None
        raise RuntimeError("fail at entry")

    session = MagicMock(spec=AsyncSession)
    composer = SQLAlchemyAsyncServiceComposition.starting_with(cleanup_provider).add(failing_provider)

    with pytest.raises(RuntimeError, match="fail at entry"):
        async with composer.open(session=session):
            pass

    assert cleanup_ran


@pytest.mark.asyncio
async def test_user_exception_inside_block_closes_entered_providers() -> None:
    cleanup_ran = False

    async def cleanup_provider(session: AsyncSession) -> AsyncGenerator[FakeServiceA, None]:
        try:
            yield FakeServiceA(session=session)
        finally:
            nonlocal cleanup_ran
            cleanup_ran = True

    session = MagicMock(spec=AsyncSession)

    async def raise_user_error() -> None:
        async with SQLAlchemyAsyncServiceComposition.starting_with(cleanup_provider).open(session=session):
            raise ValueError("user error")

    with pytest.raises(ValueError, match="user error"):
        await raise_user_error()

    assert cleanup_ran


def test_service_with_session_protocol_recognizes_session_keyword_services() -> None:
    class GoodService:
        def __init__(self, *, session: AsyncSession) -> None:
            self.session = session

    service = GoodService(session=MagicMock(spec=AsyncSession))

    assert isinstance(service, ServiceWithSession)


# ---- sync variants ----


def test_compose_sync_services_returns_typed_composition() -> None:
    session = MagicMock(spec=Session)
    composer = compose_sync_services(FakeServiceA)

    with composer.open(session=session) as (a,):
        assert isinstance(a, FakeServiceA)
        assert a.session is session


def test_provide_sync_services_shorthand() -> None:
    session = MagicMock(spec=Session)

    def p1(s: Session) -> Generator[FakeServiceA, None, None]:
        yield FakeServiceA(session=s)  # type: ignore[arg-type]

    with provide_sync_services(p1, FakeServiceB, session=cast("Session", session)) as (a, b):
        assert isinstance(a, FakeServiceA)
        assert isinstance(b, FakeServiceB)
        assert a.session is b.session is session


def test_sync_partial_failure_closes_entered_providers() -> None:
    cleanup_ran = False

    def cleanup_provider(session: Session) -> Generator[FakeServiceA, None, None]:
        try:
            yield FakeServiceA(session=session)  # type: ignore[arg-type]
        finally:
            nonlocal cleanup_ran
            cleanup_ran = True

    def failing_provider(session: Session) -> Generator[Any, None, None]:
        if repr(session) == "unused":
            yield None
        raise RuntimeError("fail at entry")

    session = MagicMock(spec=Session)
    composer = SQLAlchemySyncServiceComposition.starting_with(cleanup_provider).add(failing_provider)

    with pytest.raises(RuntimeError, match="fail at entry"):
        with composer.open(session=session):
            pass

    assert cleanup_ran
