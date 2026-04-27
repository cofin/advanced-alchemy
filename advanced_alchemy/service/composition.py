"""Framework-agnostic service composition primitives.

Example:
    Compose providers that yield services for a caller-owned async session:

    .. code-block:: python

        async with (
            compose_async_services(UserService)
            .add(RoleService)
            .open(session=db_session)
        ) as (users, roles):
            await users.create(data)
            await roles.assign_default_role(data)
"""

from collections.abc import AsyncGenerator, Generator
from contextlib import (
    AbstractAsyncContextManager,
    AbstractContextManager,
    AsyncExitStack,
    ExitStack,
    asynccontextmanager,
    contextmanager,
)
from typing import TYPE_CHECKING, Any, Generic, cast, overload

from typing_extensions import TypeVar, TypeVarTuple, Unpack

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import Session

    from advanced_alchemy.service._typing import (
        SQLAlchemyAsyncServiceCompositionInput,
        SQLAlchemyAsyncServiceProvider,
        SQLAlchemySyncServiceCompositionInput,
        SQLAlchemySyncServiceProvider,
    )

__all__ = (
    "SQLAlchemyAsyncServiceComposition",
    "SQLAlchemySyncServiceComposition",
    "compose_async_services",
    "compose_sync_services",
    "provide_async_services",
    "provide_sync_services",
)

T = TypeVar("T")
Ts = TypeVarTuple("Ts")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")
T5 = TypeVar("T5")
T6 = TypeVar("T6")
T7 = TypeVar("T7")
T8 = TypeVar("T8")
T9 = TypeVar("T9")
T10 = TypeVar("T10")


@asynccontextmanager
async def _aclose_generator(
    generator: "AsyncGenerator[Any, None]",
) -> "AsyncGenerator[AsyncGenerator[Any, None], None]":
    # Python 3.9 lacks contextlib.aclosing; replace this helper when 3.9 support is dropped.
    try:
        yield generator
    finally:
        await generator.aclose()


@contextmanager
def _close_generator(
    generator: "Generator[Any, None, None]",
) -> "Generator[Generator[Any, None, None], None, None]":
    try:
        yield generator
    finally:
        generator.close()


def _ensure_provider(input_item: "SQLAlchemyAsyncServiceCompositionInput[T]") -> "SQLAlchemyAsyncServiceProvider[T]":
    """Internal helper to wrap service classes in a provider generator."""
    if isinstance(input_item, type):

        async def provider(session: "AsyncSession") -> AsyncGenerator[T, None]:
            if hasattr(input_item, "new"):
                async with cast("Any", input_item).new(session=session) as service:
                    yield service
            else:
                yield cast("Any", input_item)(session=session)

        return provider
    return input_item


def _ensure_provider_sync(
    input_item: "SQLAlchemySyncServiceCompositionInput[T]",
) -> "SQLAlchemySyncServiceProvider[T]":
    """Internal helper to wrap service classes in a sync provider generator."""
    if isinstance(input_item, type):

        def provider(session: "Session") -> Generator[T, None, None]:
            yield cast("Any", input_item)(session=session)

        return provider
    return input_item


class SQLAlchemyAsyncServiceComposition(Generic[Unpack[Ts]]):
    """Builder for composing services with a shared async session.

    Typing-accurate at unbounded arity via PEP 646's accumulation pattern.
    """

    __slots__ = ("_providers",)

    def __init__(self, _providers: "tuple[SQLAlchemyAsyncServiceProvider[Any], ...]" = ()) -> None:
        self._providers = _providers

    @classmethod
    def starting_with(
        cls, input_item: "SQLAlchemyAsyncServiceCompositionInput[T]"
    ) -> "SQLAlchemyAsyncServiceComposition[T]":
        """Begin a composition with the first provider or service class."""
        return cast("SQLAlchemyAsyncServiceComposition[T]", cls((_ensure_provider(input_item),)))

    def add(
        self, input_item: "SQLAlchemyAsyncServiceCompositionInput[T]"
    ) -> "SQLAlchemyAsyncServiceComposition[Unpack[Ts], T]":
        """Append a provider or service class, extending the service tuple by one position."""
        return cast(
            "SQLAlchemyAsyncServiceComposition[Unpack[Ts], T]",
            SQLAlchemyAsyncServiceComposition((*self._providers, _ensure_provider(input_item))),
        )

    @asynccontextmanager
    async def open(self, *, session: "AsyncSession") -> "AsyncGenerator[tuple[Unpack[Ts]], None]":
        """Enter all providers on ``session`` and yield their services.

        The session lifecycle remains owned by the caller. Entered provider
        generators are closed in reverse order on normal exit, user exception,
        or partial-entry failure.
        """
        services: list[Any] = []
        async with AsyncExitStack() as stack:
            for provider in self._providers:
                generator = await stack.enter_async_context(_aclose_generator(provider(session)))
                services.append(await generator.__anext__())
            yield cast("tuple[Unpack[Ts]]", tuple(services))


class SQLAlchemySyncServiceComposition(Generic[Unpack[Ts]]):
    """Builder for composing services with a shared sync session.

    Typing-accurate at unbounded arity via PEP 646's accumulation pattern.
    """

    __slots__ = ("_providers",)

    def __init__(self, _providers: "tuple[SQLAlchemySyncServiceProvider[Any], ...]" = ()) -> None:
        self._providers = _providers

    @classmethod
    def starting_with(
        cls, input_item: "SQLAlchemySyncServiceCompositionInput[T]"
    ) -> "SQLAlchemySyncServiceComposition[T]":
        """Begin a sync composition with the first provider or service class."""
        return cast("SQLAlchemySyncServiceComposition[T]", cls((_ensure_provider_sync(input_item),)))

    def add(
        self, input_item: "SQLAlchemySyncServiceCompositionInput[T]"
    ) -> "SQLAlchemySyncServiceComposition[Unpack[Ts], T]":
        """Append a sync provider or service class, extending the service tuple by one position."""
        return cast(
            "SQLAlchemySyncServiceComposition[Unpack[Ts], T]",
            SQLAlchemySyncServiceComposition((*self._providers, _ensure_provider_sync(input_item))),
        )

    @contextmanager
    def open(self, *, session: "Session") -> "Generator[tuple[Unpack[Ts]], None, None]":
        """Enter all sync providers on ``session`` and yield their services.

        The session lifecycle remains owned by the caller. Entered provider
        generators are closed in reverse order on normal exit, user exception,
        or partial-entry failure.
        """
        services: list[Any] = []
        with ExitStack() as stack:
            for provider in self._providers:
                generator = stack.enter_context(_close_generator(provider(session)))
                services.append(next(generator))
            yield cast("tuple[Unpack[Ts]]", tuple(services))


def compose_async_services(
    input_item: "SQLAlchemyAsyncServiceCompositionInput[T]",
) -> "SQLAlchemyAsyncServiceComposition[T]":
    """Start a service composition chain.

    Args:
        input_item: Either a service class or a provider generator.

    Returns:
        A :class:`SQLAlchemyAsyncServiceComposition` builder seeded with the input.
    """
    return SQLAlchemyAsyncServiceComposition[T].starting_with(input_item)


def compose_sync_services(
    input_item: "SQLAlchemySyncServiceCompositionInput[T]",
) -> "SQLAlchemySyncServiceComposition[T]":
    """Start a sync service composition chain.

    Args:
        input_item: Either a service class or a sync provider generator.

    Returns:
        A :class:`SQLAlchemySyncServiceComposition` builder seeded with the input.
    """
    return SQLAlchemySyncServiceComposition[T].starting_with(input_item)


@overload
def provide_async_services(
    i1: "SQLAlchemyAsyncServiceCompositionInput[T1]",
    /,
    *,
    session: "AsyncSession",
) -> AbstractAsyncContextManager[tuple[T1]]: ...


@overload
def provide_async_services(
    i1: "SQLAlchemyAsyncServiceCompositionInput[T1]",
    i2: "SQLAlchemyAsyncServiceCompositionInput[T2]",
    /,
    *,
    session: "AsyncSession",
) -> AbstractAsyncContextManager[tuple[T1, T2]]: ...


@overload
def provide_async_services(
    i1: "SQLAlchemyAsyncServiceCompositionInput[T1]",
    i2: "SQLAlchemyAsyncServiceCompositionInput[T2]",
    i3: "SQLAlchemyAsyncServiceCompositionInput[T3]",
    /,
    *,
    session: "AsyncSession",
) -> AbstractAsyncContextManager[tuple[T1, T2, T3]]: ...


@overload
def provide_async_services(
    i1: "SQLAlchemyAsyncServiceCompositionInput[T1]",
    i2: "SQLAlchemyAsyncServiceCompositionInput[T2]",
    i3: "SQLAlchemyAsyncServiceCompositionInput[T3]",
    i4: "SQLAlchemyAsyncServiceCompositionInput[T4]",
    /,
    *,
    session: "AsyncSession",
) -> AbstractAsyncContextManager[tuple[T1, T2, T3, T4]]: ...


@overload
def provide_async_services(
    i1: "SQLAlchemyAsyncServiceCompositionInput[T1]",
    i2: "SQLAlchemyAsyncServiceCompositionInput[T2]",
    i3: "SQLAlchemyAsyncServiceCompositionInput[T3]",
    i4: "SQLAlchemyAsyncServiceCompositionInput[T4]",
    i5: "SQLAlchemyAsyncServiceCompositionInput[T5]",
    /,
    *,
    session: "AsyncSession",
) -> AbstractAsyncContextManager[tuple[T1, T2, T3, T4, T5]]: ...


@overload
def provide_async_services(
    i1: "SQLAlchemyAsyncServiceCompositionInput[T1]",
    i2: "SQLAlchemyAsyncServiceCompositionInput[T2]",
    i3: "SQLAlchemyAsyncServiceCompositionInput[T3]",
    i4: "SQLAlchemyAsyncServiceCompositionInput[T4]",
    i5: "SQLAlchemyAsyncServiceCompositionInput[T5]",
    i6: "SQLAlchemyAsyncServiceCompositionInput[T6]",
    /,
    *,
    session: "AsyncSession",
) -> AbstractAsyncContextManager[tuple[T1, T2, T3, T4, T5, T6]]: ...


@overload
def provide_async_services(
    i1: "SQLAlchemyAsyncServiceCompositionInput[T1]",
    i2: "SQLAlchemyAsyncServiceCompositionInput[T2]",
    i3: "SQLAlchemyAsyncServiceCompositionInput[T3]",
    i4: "SQLAlchemyAsyncServiceCompositionInput[T4]",
    i5: "SQLAlchemyAsyncServiceCompositionInput[T5]",
    i6: "SQLAlchemyAsyncServiceCompositionInput[T6]",
    i7: "SQLAlchemyAsyncServiceCompositionInput[T7]",
    /,
    *,
    session: "AsyncSession",
) -> AbstractAsyncContextManager[tuple[T1, T2, T3, T4, T5, T6, T7]]: ...


@overload
def provide_async_services(
    i1: "SQLAlchemyAsyncServiceCompositionInput[T1]",
    i2: "SQLAlchemyAsyncServiceCompositionInput[T2]",
    i3: "SQLAlchemyAsyncServiceCompositionInput[T3]",
    i4: "SQLAlchemyAsyncServiceCompositionInput[T4]",
    i5: "SQLAlchemyAsyncServiceCompositionInput[T5]",
    i6: "SQLAlchemyAsyncServiceCompositionInput[T6]",
    i7: "SQLAlchemyAsyncServiceCompositionInput[T7]",
    i8: "SQLAlchemyAsyncServiceCompositionInput[T8]",
    /,
    *,
    session: "AsyncSession",
) -> AbstractAsyncContextManager[tuple[T1, T2, T3, T4, T5, T6, T7, T8]]: ...


@overload
def provide_async_services(
    i1: "SQLAlchemyAsyncServiceCompositionInput[T1]",
    i2: "SQLAlchemyAsyncServiceCompositionInput[T2]",
    i3: "SQLAlchemyAsyncServiceCompositionInput[T3]",
    i4: "SQLAlchemyAsyncServiceCompositionInput[T4]",
    i5: "SQLAlchemyAsyncServiceCompositionInput[T5]",
    i6: "SQLAlchemyAsyncServiceCompositionInput[T6]",
    i7: "SQLAlchemyAsyncServiceCompositionInput[T7]",
    i8: "SQLAlchemyAsyncServiceCompositionInput[T8]",
    i9: "SQLAlchemyAsyncServiceCompositionInput[T9]",
    /,
    *,
    session: "AsyncSession",
) -> AbstractAsyncContextManager[tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9]]: ...


@overload
def provide_async_services(
    i1: "SQLAlchemyAsyncServiceCompositionInput[T1]",
    i2: "SQLAlchemyAsyncServiceCompositionInput[T2]",
    i3: "SQLAlchemyAsyncServiceCompositionInput[T3]",
    i4: "SQLAlchemyAsyncServiceCompositionInput[T4]",
    i5: "SQLAlchemyAsyncServiceCompositionInput[T5]",
    i6: "SQLAlchemyAsyncServiceCompositionInput[T6]",
    i7: "SQLAlchemyAsyncServiceCompositionInput[T7]",
    i8: "SQLAlchemyAsyncServiceCompositionInput[T8]",
    i9: "SQLAlchemyAsyncServiceCompositionInput[T9]",
    i10: "SQLAlchemyAsyncServiceCompositionInput[T10]",
    /,
    *,
    session: "AsyncSession",
) -> AbstractAsyncContextManager[tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10]]: ...


@asynccontextmanager
async def provide_async_services(
    *inputs: "SQLAlchemyAsyncServiceCompositionInput[Any]",
    session: "AsyncSession",
) -> AsyncGenerator[tuple[Any, ...], None]:
    """Compose and open async services in one call.

    Args:
        *inputs: Service classes or async provider generators.
        session: The shared async session to provide to each service.

    Yields:
        A tuple of instantiated services in the same order as inputs.
    """
    if not inputs:
        msg = "At least one service provider or class is required"
        raise ValueError(msg)

    composer = compose_async_services(inputs[0])
    for item in inputs[1:]:
        composer = composer.add(item)

    async with composer.open(session=session) as services:
        yield services


@overload
def provide_sync_services(
    i1: "SQLAlchemySyncServiceCompositionInput[T1]",
    /,
    *,
    session: "Session",
) -> AbstractContextManager[tuple[T1]]: ...


@overload
def provide_sync_services(
    i1: "SQLAlchemySyncServiceCompositionInput[T1]",
    i2: "SQLAlchemySyncServiceCompositionInput[T2]",
    /,
    *,
    session: "Session",
) -> AbstractContextManager[tuple[T1, T2]]: ...


@overload
def provide_sync_services(
    i1: "SQLAlchemySyncServiceCompositionInput[T1]",
    i2: "SQLAlchemySyncServiceCompositionInput[T2]",
    i3: "SQLAlchemySyncServiceCompositionInput[T3]",
    /,
    *,
    session: "Session",
) -> AbstractContextManager[tuple[T1, T2, T3]]: ...


@overload
def provide_sync_services(
    i1: "SQLAlchemySyncServiceCompositionInput[T1]",
    i2: "SQLAlchemySyncServiceCompositionInput[T2]",
    i3: "SQLAlchemySyncServiceCompositionInput[T3]",
    i4: "SQLAlchemySyncServiceCompositionInput[T4]",
    /,
    *,
    session: "Session",
) -> AbstractContextManager[tuple[T1, T2, T3, T4]]: ...


@overload
def provide_sync_services(
    i1: "SQLAlchemySyncServiceCompositionInput[T1]",
    i2: "SQLAlchemySyncServiceCompositionInput[T2]",
    i3: "SQLAlchemySyncServiceCompositionInput[T3]",
    i4: "SQLAlchemySyncServiceCompositionInput[T4]",
    i5: "SQLAlchemySyncServiceCompositionInput[T5]",
    /,
    *,
    session: "Session",
) -> AbstractContextManager[tuple[T1, T2, T3, T4, T5]]: ...


@overload
def provide_sync_services(
    i1: "SQLAlchemySyncServiceCompositionInput[T1]",
    i2: "SQLAlchemySyncServiceCompositionInput[T2]",
    i3: "SQLAlchemySyncServiceCompositionInput[T3]",
    i4: "SQLAlchemySyncServiceCompositionInput[T4]",
    i5: "SQLAlchemySyncServiceCompositionInput[T5]",
    i6: "SQLAlchemySyncServiceCompositionInput[T6]",
    /,
    *,
    session: "Session",
) -> AbstractContextManager[tuple[T1, T2, T3, T4, T5, T6]]: ...


@overload
def provide_sync_services(
    i1: "SQLAlchemySyncServiceCompositionInput[T1]",
    i2: "SQLAlchemySyncServiceCompositionInput[T2]",
    i3: "SQLAlchemySyncServiceCompositionInput[T3]",
    i4: "SQLAlchemySyncServiceCompositionInput[T4]",
    i5: "SQLAlchemySyncServiceCompositionInput[T5]",
    i6: "SQLAlchemySyncServiceCompositionInput[T6]",
    i7: "SQLAlchemySyncServiceCompositionInput[T7]",
    /,
    *,
    session: "Session",
) -> AbstractContextManager[tuple[T1, T2, T3, T4, T5, T6, T7]]: ...


@overload
def provide_sync_services(
    i1: "SQLAlchemySyncServiceCompositionInput[T1]",
    i2: "SQLAlchemySyncServiceCompositionInput[T2]",
    i3: "SQLAlchemySyncServiceCompositionInput[T3]",
    i4: "SQLAlchemySyncServiceCompositionInput[T4]",
    i5: "SQLAlchemySyncServiceCompositionInput[T5]",
    i6: "SQLAlchemySyncServiceCompositionInput[T6]",
    i7: "SQLAlchemySyncServiceCompositionInput[T7]",
    i8: "SQLAlchemySyncServiceCompositionInput[T8]",
    /,
    *,
    session: "Session",
) -> AbstractContextManager[tuple[T1, T2, T3, T4, T5, T6, T7, T8]]: ...


@overload
def provide_sync_services(
    i1: "SQLAlchemySyncServiceCompositionInput[T1]",
    i2: "SQLAlchemySyncServiceCompositionInput[T2]",
    i3: "SQLAlchemySyncServiceCompositionInput[T3]",
    i4: "SQLAlchemySyncServiceCompositionInput[T4]",
    i5: "SQLAlchemySyncServiceCompositionInput[T5]",
    i6: "SQLAlchemySyncServiceCompositionInput[T6]",
    i7: "SQLAlchemySyncServiceCompositionInput[T7]",
    i8: "SQLAlchemySyncServiceCompositionInput[T8]",
    i9: "SQLAlchemySyncServiceCompositionInput[T9]",
    /,
    *,
    session: "Session",
) -> AbstractContextManager[tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9]]: ...


@overload
def provide_sync_services(
    i1: "SQLAlchemySyncServiceCompositionInput[T1]",
    i2: "SQLAlchemySyncServiceCompositionInput[T2]",
    i3: "SQLAlchemySyncServiceCompositionInput[T3]",
    i4: "SQLAlchemySyncServiceCompositionInput[T4]",
    i5: "SQLAlchemySyncServiceCompositionInput[T5]",
    i6: "SQLAlchemySyncServiceCompositionInput[T6]",
    i7: "SQLAlchemySyncServiceCompositionInput[T7]",
    i8: "SQLAlchemySyncServiceCompositionInput[T8]",
    i9: "SQLAlchemySyncServiceCompositionInput[T9]",
    i10: "SQLAlchemySyncServiceCompositionInput[T10]",
    /,
    *,
    session: "Session",
) -> AbstractContextManager[tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10]]: ...


@contextmanager
def provide_sync_services(
    *inputs: "SQLAlchemySyncServiceCompositionInput[Any]",
    session: "Session",
) -> Generator[tuple[Any, ...], None, None]:
    """Compose and open sync services in one call.

    Args:
        *inputs: Service classes or sync provider generators.
        session: The shared sync session to provide to each service.

    Yields:
        A tuple of instantiated services in the same order as inputs.
    """
    if not inputs:
        msg = "At least one service provider or class is required"
        raise ValueError(msg)

    composer = compose_sync_services(inputs[0])
    for item in inputs[1:]:
        composer = composer.add(item)

    with composer.open(session=session) as services:
        yield services
