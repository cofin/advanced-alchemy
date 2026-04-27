"""Static-typing assertions for Litestar provide_async_services overloads."""

from collections.abc import AsyncGenerator
from contextlib import AbstractAsyncContextManager
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

from typing_extensions import assert_type

from advanced_alchemy.extensions.litestar.providers import provide_async_services

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class S1: ...


class S2: ...


class S3: ...


async def p1(s: "AsyncSession") -> AsyncGenerator[S1, None]:
    yield S1()


async def p2(s: "AsyncSession") -> AsyncGenerator[S2, None]:
    yield S2()


async def p3(s: "AsyncSession") -> AsyncGenerator[S3, None]:
    yield S3()


def test_arity_one() -> None:
    cfg: Any = MagicMock()
    cm = provide_async_services(p1, config=cfg)
    assert_type(cm, AbstractAsyncContextManager[tuple[S1]])


def test_arity_three() -> None:
    cfg: Any = MagicMock()
    cm = provide_async_services(p1, p2, p3, config=cfg)
    assert_type(cm, AbstractAsyncContextManager[tuple[S1, S2, S3]])


def test_class_arity_two() -> None:
    class ServiceA:
        def __init__(self, *, session: "AsyncSession") -> None: ...

    cfg: Any = MagicMock()
    cm = provide_async_services(ServiceA, p2, config=cfg)
    assert_type(cm, AbstractAsyncContextManager[tuple[ServiceA, S2]])
