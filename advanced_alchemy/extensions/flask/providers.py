from collections.abc import Generator
from contextlib import AbstractContextManager, contextmanager
from typing import TYPE_CHECKING, Any, Optional, TypeVar, overload

from flask import g, has_app_context

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from advanced_alchemy.extensions.flask.config import SQLAlchemySyncConfig
    from advanced_alchemy.service import SQLAlchemySyncServiceCompositionInput

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
def provide_sync_services(
    i1: "SQLAlchemySyncServiceCompositionInput[T1]",
    /,
    *,
    config: "SQLAlchemySyncConfig",
    session: "Optional[Session]" = None,
) -> AbstractContextManager[tuple[T1]]: ...


@overload
def provide_sync_services(
    i1: "SQLAlchemySyncServiceCompositionInput[T1]",
    i2: "SQLAlchemySyncServiceCompositionInput[T2]",
    /,
    *,
    config: "SQLAlchemySyncConfig",
    session: "Optional[Session]" = None,
) -> AbstractContextManager[tuple[T1, T2]]: ...


@overload
def provide_sync_services(
    i1: "SQLAlchemySyncServiceCompositionInput[T1]",
    i2: "SQLAlchemySyncServiceCompositionInput[T2]",
    i3: "SQLAlchemySyncServiceCompositionInput[T3]",
    /,
    *,
    config: "SQLAlchemySyncConfig",
    session: "Optional[Session]" = None,
) -> AbstractContextManager[tuple[T1, T2, T3]]: ...


@overload
def provide_sync_services(
    i1: "SQLAlchemySyncServiceCompositionInput[T1]",
    i2: "SQLAlchemySyncServiceCompositionInput[T2]",
    i3: "SQLAlchemySyncServiceCompositionInput[T3]",
    i4: "SQLAlchemySyncServiceCompositionInput[T4]",
    /,
    *,
    config: "SQLAlchemySyncConfig",
    session: "Optional[Session]" = None,
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
    config: "SQLAlchemySyncConfig",
    session: "Optional[Session]" = None,
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
    config: "SQLAlchemySyncConfig",
    session: "Optional[Session]" = None,
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
    config: "SQLAlchemySyncConfig",
    session: "Optional[Session]" = None,
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
    config: "SQLAlchemySyncConfig",
    session: "Optional[Session]" = None,
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
    config: "SQLAlchemySyncConfig",
    session: "Optional[Session]" = None,
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
    config: "SQLAlchemySyncConfig",
    session: "Optional[Session]" = None,
) -> AbstractContextManager[tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10]]: ...


@contextmanager
def provide_sync_services(
    *inputs: "SQLAlchemySyncServiceCompositionInput[Any]",
    config: "SQLAlchemySyncConfig",
    session: "Optional[Session]" = None,
) -> Generator[tuple[Any, ...], None, None]:
    """Compose and open sync services in one call — Flask-aware.

    This function handles three modes of session resolution:

    1.  **Explicit session**: If ``session`` is provided, it is used directly.
        The caller owns the session lifecycle.
    2.  **App-scoped session**: If we are inside a Flask application context,
        the session is resolved from ``flask.g.advanced_alchemy_session_<bind_key>``.
        This assumes the extension's middleware or manual session management is active.
    3.  **Standalone session**: If neither is provided (or not in app context),
        a new session is opened via ``config.get_session()`` and closed
        after the services are yielded.

    Args:
        *inputs: Service classes or provider generators.
        config: The SQLAlchemy configuration to use for session resolution.
        session: An optional explicit session to use.

    Yields:
        A tuple of instantiated services in the same order as inputs.

    Raises:
        ValueError: If no inputs are provided.
    """
    from advanced_alchemy.service import SQLAlchemySyncServiceComposition

    if not inputs:
        msg = "At least one service provider or class is required"
        raise ValueError(msg)

    composer = SQLAlchemySyncServiceComposition.starting_with(inputs[0])
    for item in inputs[1:]:
        composer = composer.add(item)

    if session is not None:
        with composer.open(session=session) as services:
            yield services
    elif has_app_context():
        bind_key = config.bind_key or "default"
        session_key = f"advanced_alchemy_session_{bind_key}"
        sess = getattr(g, session_key, None)
        if sess is not None:
            with composer.open(session=sess) as services:
                yield services
        else:
            # Not in g, maybe they want us to open one for them?
            # For now, let's fallback to standalone if not in g even if in app context
            with config.get_session() as sess, composer.open(session=sess) as services:
                yield services
    else:
        with config.get_session() as sess, composer.open(session=sess) as services:
            yield services
