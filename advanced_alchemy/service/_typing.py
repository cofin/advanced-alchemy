"""Service-side typing surface."""

from collections.abc import AsyncGenerator, Callable, Generator
from typing import TYPE_CHECKING, Protocol, Union, runtime_checkable

from typing_extensions import TypeAlias, TypeVar

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import Session

__all__ = (
    "ModelWithSlug",
    "SQLAlchemyAsyncServiceCompositionInput",
    "SQLAlchemyAsyncServiceProvider",
    "SQLAlchemySyncServiceCompositionInput",
    "SQLAlchemySyncServiceProvider",
    "ServiceWithSession",
)

T = TypeVar("T")


@runtime_checkable
class ModelWithSlug(Protocol):
    """Protocol for models with a slug attribute."""

    slug: str


SQLAlchemyAsyncServiceProvider: TypeAlias = Callable[["AsyncSession"], AsyncGenerator[T, None]]
"""Callable that yields a service instance for a session."""

SQLAlchemyAsyncServiceCompositionInput = Union[SQLAlchemyAsyncServiceProvider[T], type[T]]
"""Input type for composition: either a provider generator or a service class."""

SQLAlchemySyncServiceProvider: TypeAlias = Callable[["Session"], Generator[T, None, None]]
"""Callable that yields a service instance for a sync session."""

SQLAlchemySyncServiceCompositionInput = Union[SQLAlchemySyncServiceProvider[T], type[T]]
"""Input type for sync composition: either a sync provider generator or a service class."""


@runtime_checkable
class ServiceWithSession(Protocol):
    """Structural protocol for services constructible with ``session=``."""

    def __init__(self, *, session: "AsyncSession") -> None: ...
