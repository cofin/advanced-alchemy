"""Tests for Litestar provide_async_services — three operating modes."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any
from unittest.mock import MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from advanced_alchemy.extensions.litestar.providers import provide_async_services

pytestmark = pytest.mark.anyio


class FakeService:
    def __init__(self, *, session: AsyncSession) -> None:
        self.session = session


async def fake_provider(session: AsyncSession) -> AsyncGenerator[FakeService, None]:
    yield FakeService(session=session)


# ---- guard rails ----


async def test_raises_on_both_session_and_connection() -> None:
    cfg = MagicMock()
    sess = MagicMock(spec=AsyncSession)
    conn = MagicMock()
    with pytest.raises(ValueError, match="Cannot provide both"):
        async with provide_async_services(fake_provider, config=cfg, session=sess, connection=conn):
            pass


async def test_raises_on_no_providers() -> None:
    cfg = MagicMock()
    with pytest.raises(ValueError, match="At least one service provider"):
        async with provide_async_services(config=cfg):  # type: ignore[call-overload]
            pass


# ---- mode 1: explicit session ----


async def test_explicit_session_mode() -> None:
    cfg = MagicMock()
    sess = MagicMock(spec=AsyncSession)
    async with provide_async_services(fake_provider, config=cfg, session=sess) as (svc,):
        assert isinstance(svc, FakeService)
        assert svc.session is sess


# ---- mode 2: connection-scoped ----


async def test_connection_scoped_mode() -> None:
    cfg = MagicMock()
    sess = MagicMock(spec=AsyncSession)
    cfg.provide_session = MagicMock(return_value=sess)
    conn = MagicMock()
    conn.app.state = MagicMock()
    conn.scope = MagicMock()
    async with provide_async_services(fake_provider, config=cfg, connection=conn) as (svc,):
        assert svc.session is sess
        cfg.provide_session.assert_called_once_with(conn.app.state, conn.scope)


# ---- mode 3: standalone ----


async def test_standalone_mode() -> None:
    cfg = MagicMock()
    sess = MagicMock(spec=AsyncSession)

    @asynccontextmanager
    async def _gen() -> AsyncGenerator[Any, None]:
        yield sess

    cfg.get_session = _gen
    async with provide_async_services(fake_provider, config=cfg) as (svc,):
        assert svc.session is sess


# ---- multi-service shared session ----


async def test_multiple_services_share_session() -> None:
    class S1:
        def __init__(self, *, session: AsyncSession) -> None:
            self.session = session

    class S2:
        def __init__(self, *, session: AsyncSession) -> None:
            self.session = session

    async def p1(s: AsyncSession) -> AsyncGenerator[S1, None]:
        yield S1(session=s)

    async def p2(s: AsyncSession) -> AsyncGenerator[S2, None]:
        yield S2(session=s)

    cfg = MagicMock()
    sess = MagicMock(spec=AsyncSession)
    async with provide_async_services(p1, p2, config=cfg, session=sess) as (svc1, svc2):
        assert svc1.session is svc2.session is sess


# ---- partial failure cleanup ----


async def test_partial_failure_cleanup() -> None:
    cleaned = False

    async def cleanup_provider(s: AsyncSession) -> AsyncGenerator[FakeService, None]:
        try:
            yield FakeService(session=s)
        finally:
            nonlocal cleaned
            cleaned = True

    async def failing_provider(s: AsyncSession) -> AsyncGenerator[Any, None]:
        if repr(s) == "unused":
            yield
        raise RuntimeError("boom")

    cfg = MagicMock()
    sess = MagicMock(spec=AsyncSession)
    with pytest.raises(RuntimeError, match="boom"):
        async with provide_async_services(cleanup_provider, failing_provider, config=cfg, session=sess):
            pass
    assert cleaned


# ---- direct class injection ----


async def test_direct_class_injection() -> None:
    cfg = MagicMock()
    sess = MagicMock(spec=AsyncSession)
    async with provide_async_services(FakeService, config=cfg, session=sess) as (svc,):
        assert isinstance(svc, FakeService)
        assert svc.session is sess
