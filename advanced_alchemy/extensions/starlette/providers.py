from collections.abc import AsyncGenerator
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import TYPE_CHECKING, Any, Optional, TypeVar, overload

if TYPE_CHECKING:
    from starlette.requests import Request

    from advanced_alchemy.extensions.starlette.config import SQLAlchemyAsyncConfig
    from advanced_alchemy.service import SQLAlchemyAsyncServiceCompositionInput

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


@overload
def provide_async_services(
    i1: "SQLAlchemyAsyncServiceCompositionInput[T1]",
    /,
    *,
    config: "SQLAlchemyAsyncConfig",
    session: "Optional[Any]" = None,
    request: "Optional[Request]" = None,
) -> AbstractAsyncContextManager[tuple[T1]]: ...


@overload
def provide_async_services(
    i1: "SQLAlchemyAsyncServiceCompositionInput[T1]",
    i2: "SQLAlchemyAsyncServiceCompositionInput[T2]",
    /,
    *,
    config: "SQLAlchemyAsyncConfig",
    session: "Optional[Any]" = None,
    request: "Optional[Request]" = None,
) -> AbstractAsyncContextManager[tuple[T1, T2]]: ...


@overload
def provide_async_services(
    i1: "SQLAlchemyAsyncServiceCompositionInput[T1]",
    i2: "SQLAlchemyAsyncServiceCompositionInput[T2]",
    i3: "SQLAlchemyAsyncServiceCompositionInput[T3]",
    /,
    *,
    config: "SQLAlchemyAsyncConfig",
    session: "Optional[Any]" = None,
    request: "Optional[Request]" = None,
) -> AbstractAsyncContextManager[tuple[T1, T2, T3]]: ...


@overload
def provide_async_services(
    i1: "SQLAlchemyAsyncServiceCompositionInput[T1]",
    i2: "SQLAlchemyAsyncServiceCompositionInput[T2]",
    i3: "SQLAlchemyAsyncServiceCompositionInput[T3]",
    i4: "SQLAlchemyAsyncServiceCompositionInput[T4]",
    /,
    *,
    config: "SQLAlchemyAsyncConfig",
    session: "Optional[Any]" = None,
    request: "Optional[Request]" = None,
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
    config: "SQLAlchemyAsyncConfig",
    session: "Optional[Any]" = None,
    request: "Optional[Request]" = None,
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
    config: "SQLAlchemyAsyncConfig",
    session: "Optional[Any]" = None,
    request: "Optional[Request]" = None,
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
    config: "SQLAlchemyAsyncConfig",
    session: "Optional[Any]" = None,
    request: "Optional[Request]" = None,
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
    config: "SQLAlchemyAsyncConfig",
    session: "Optional[Any]" = None,
    request: "Optional[Request]" = None,
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
    config: "SQLAlchemyAsyncConfig",
    session: "Optional[Any]" = None,
    request: "Optional[Request]" = None,
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
    config: "SQLAlchemyAsyncConfig",
    session: "Optional[Any]" = None,
    request: "Optional[Request]" = None,
) -> AbstractAsyncContextManager[tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10]]: ...


@asynccontextmanager
async def provide_async_services(
    *inputs: "SQLAlchemyAsyncServiceCompositionInput[Any]",
    config: "SQLAlchemyAsyncConfig",
    session: "Optional[Any]" = None,
    request: "Optional[Request]" = None,
) -> AsyncGenerator[tuple[Any, ...], None]:
    """Compose and open async services in one call — Starlette-aware.

    This function handles three modes of session resolution:

    1.  **Explicit session**: If ``session`` is provided, it is used directly.
        The caller owns the session lifecycle.
    2.  **Request-scoped session**: If ``request`` is provided, the session is
        resolved from ``request.state.<session_key>``. This assumes the
        extension's middleware is active.
    3.  **Standalone session**: If neither is provided, a new session is
        opened via ``config.get_session()`` and closed after the services
        are yielded.

    Args:
        *inputs: Service classes or provider generators.
        config: The SQLAlchemy configuration to use for session resolution.
        session: An optional explicit session to use.
        request: An optional Starlette request to resolve the session from.

    Yields:
        A tuple of instantiated services in the same order as inputs.

    Raises:
        ValueError: If both 'session' and 'request' are provided.
        RuntimeError: If resolving from 'request' fails.
    """
    from advanced_alchemy.service import SQLAlchemyAsyncServiceComposition

    if session is not None and request is not None:
        msg = "Cannot provide both 'session' and 'request' — choose one"
        raise ValueError(msg)
    if not inputs:
        msg = "At least one service provider or class is required"
        raise ValueError(msg)

    composer = SQLAlchemyAsyncServiceComposition.starting_with(inputs[0])
    for item in inputs[1:]:
        composer = composer.add(item)

    if session is not None:
        async with composer.open(session=session) as services:
            yield services
    elif request is not None:
        sess = getattr(request.state, config.session_key, None)
        if sess is None:
            msg = f"No session in request.state.{config.session_key} — ensure the extension's middleware is registered"
            raise RuntimeError(msg)
        async with composer.open(session=sess) as services:
            yield services
    else:
        async with config.get_session() as sess, composer.open(session=sess) as services:
            yield services
