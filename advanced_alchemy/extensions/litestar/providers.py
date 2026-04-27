# ruff: noqa: B008
"""Application dependency providers generators.

This module contains functions to create dependency providers for services and filters.

You should not have modify this module very often and should only be invoked under normal usage.
"""

import datetime
import inspect
from collections.abc import AsyncGenerator, Callable, Generator
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    Optional,
    TypeVar,
    Union,
    cast,
    overload,
)
from uuid import UUID

from litestar.di import Provide
from litestar.params import Dependency, Parameter

from advanced_alchemy.filters import (
    BeforeAfter,
    CollectionFilter,
    FilterTypes,
    LimitOffset,
    NotInCollectionFilter,
    OrderBy,
    SearchFilter,
)
from advanced_alchemy.service import (
    Empty,
    EmptyType,
    ErrorMessages,
    LoadSpec,
    ModelT,
    SQLAlchemyAsyncRepositoryService,
    SQLAlchemyAsyncServiceComposition,
    SQLAlchemySyncRepositoryService,
)
from advanced_alchemy.utils.dependencies import DependencyCache, FieldNameType, FilterConfig, make_hashable
from advanced_alchemy.utils.singleton import SingletonMeta
from advanced_alchemy.utils.text import camelize

if TYPE_CHECKING:
    from litestar.connection import ASGIConnection
    from sqlalchemy import Select
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import Session

    from advanced_alchemy.extensions.litestar.plugins.init.config.asyncio import SQLAlchemyAsyncConfig
    from advanced_alchemy.extensions.litestar.plugins.init.config.sync import SQLAlchemySyncConfig
    from advanced_alchemy.service import SQLAlchemyAsyncServiceCompositionInput

DTorNone = Optional[datetime.datetime]
StringOrNone = Optional[str]
UuidOrNone = Optional[UUID]
IntOrNone = Optional[int]
BooleanOrNone = Optional[bool]
SortOrder = Literal["asc", "desc"]
SortOrderOrNone = Optional[SortOrder]
AsyncServiceT_co = TypeVar("AsyncServiceT_co", bound=SQLAlchemyAsyncRepositoryService[Any, Any], covariant=True)
SyncServiceT_co = TypeVar("SyncServiceT_co", bound=SQLAlchemySyncRepositoryService[Any, Any], covariant=True)

__all__ = (
    "DEPENDENCY_DEFAULTS",
    "DependencyCache",
    "DependencyDefaults",
    "FieldNameType",
    "FilterConfig",
    "SingletonMeta",
    "create_filter_dependencies",
    "create_service_dependencies",
    "create_service_provider",
    "dep_cache",
    "provide_async_services",
)

_CACHE_NAMESPACE = "advanced_alchemy.extensions.litestar.providers"


class DependencyDefaults:
    FILTERS_DEPENDENCY_KEY: str = "filters"
    """Key for the filters dependency."""
    CREATED_FILTER_DEPENDENCY_KEY: str = "created_filter"
    """Key for the created filter dependency."""
    ID_FILTER_DEPENDENCY_KEY: str = "id_filter"
    """Key for the id filter dependency."""
    LIMIT_OFFSET_FILTER_DEPENDENCY_KEY: str = "limit_offset_filter"
    """Key for the limit offset dependency."""
    UPDATED_FILTER_DEPENDENCY_KEY: str = "updated_filter"
    """Key for the updated filter dependency."""
    ORDER_BY_FILTER_DEPENDENCY_KEY: str = "order_by_filter"
    """Key for the order by dependency."""
    SEARCH_FILTER_DEPENDENCY_KEY: str = "search_filter"
    """Key for the search filter dependency."""
    DEFAULT_PAGINATION_SIZE: int = 20
    """Default pagination size."""


DEPENDENCY_DEFAULTS = DependencyDefaults()


dep_cache = DependencyCache()


@overload
def create_service_provider(
    service_class: type["AsyncServiceT_co"],
    /,
    statement: "Optional[Select[tuple[ModelT]]]" = None,
    config: "Optional[SQLAlchemyAsyncConfig]" = None,
    error_messages: "Optional[Union[ErrorMessages, EmptyType]]" = Empty,
    load: "Optional[LoadSpec]" = None,
    execution_options: "Optional[dict[str, Any]]" = None,
    uniquify: Optional[bool] = None,
    count_with_window_function: Optional[bool] = None,
) -> Callable[..., AsyncGenerator[AsyncServiceT_co, None]]: ...


@overload
def create_service_provider(
    service_class: type["SyncServiceT_co"],
    /,
    statement: "Optional[Select[tuple[ModelT]]]" = None,
    config: "Optional[SQLAlchemySyncConfig]" = None,
    error_messages: "Optional[Union[ErrorMessages, EmptyType]]" = Empty,
    load: "Optional[LoadSpec]" = None,
    execution_options: "Optional[dict[str, Any]]" = None,
    uniquify: Optional[bool] = None,
    count_with_window_function: Optional[bool] = None,
) -> Callable[..., Generator[SyncServiceT_co, None, None]]: ...


def create_service_provider(
    service_class: type[Union["AsyncServiceT_co", "SyncServiceT_co"]],
    /,
    statement: "Optional[Select[tuple[ModelT]]]" = None,
    config: "Optional[Union[SQLAlchemyAsyncConfig, SQLAlchemySyncConfig]]" = None,
    error_messages: "Optional[Union[ErrorMessages, EmptyType]]" = Empty,
    load: "Optional[LoadSpec]" = None,
    execution_options: "Optional[dict[str, Any]]" = None,
    uniquify: Optional[bool] = None,
    count_with_window_function: Optional[bool] = None,
) -> Callable[..., Union["AsyncGenerator[AsyncServiceT_co, None]", "Generator[SyncServiceT_co,None, None]"]]:
    """Create a dependency provider for a service with a configurable session key.

    Args:
        service_class: The service class inheriting from SQLAlchemyAsyncRepositoryService or SQLAlchemySyncRepositoryService.
        statement: An optional SQLAlchemy Select statement to scope the service.
        config: An optional SQLAlchemy configuration object.
        error_messages: Optional custom error messages for the service.
        load: Optional LoadSpec for eager loading relationships.
        execution_options: Optional dictionary of execution options for SQLAlchemy.
        uniquify: Optional flag to uniquify results.
        count_with_window_function: Optional flag to use window function for counting.

    Returns:
        A dependency provider function suitable for Litestar's DI system.
    """

    session_dependency_key = config.session_dependency_key if config else "db_session"

    if issubclass(service_class, SQLAlchemyAsyncRepositoryService) or service_class is SQLAlchemyAsyncRepositoryService:  # type: ignore[comparison-overlap]
        session_type_annotation = "Optional[AsyncSession]"
        return_type_annotation = AsyncGenerator[service_class, None]  # type: ignore[valid-type]

        async def provide_service_async(*args: Any, **kwargs: Any) -> "AsyncGenerator[AsyncServiceT_co, None]":
            db_session = cast("Optional[AsyncSession]", args[0] if args else kwargs.get(session_dependency_key))
            async with service_class.new(  # type: ignore[union-attr]
                session=db_session,  # type: ignore[arg-type]
                statement=statement,
                config=cast("Optional[SQLAlchemyAsyncConfig]", config),  # type: ignore[arg-type]
                error_messages=error_messages,
                load=load,
                execution_options=execution_options,
                uniquify=uniquify,
                count_with_window_function=count_with_window_function,
            ) as service:
                yield service

        session_param = inspect.Parameter(
            name=session_dependency_key,
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            default=Dependency(skip_validation=True),
            annotation=session_type_annotation,
        )

        provider_signature = inspect.Signature(
            parameters=[session_param],
            return_annotation=return_type_annotation,
        )
        provide_service_async.__signature__ = provider_signature  # type: ignore[attr-defined]
        provide_service_async.__annotations__ = {
            session_dependency_key: session_type_annotation,
            "return": return_type_annotation,
        }
        return provide_service_async
    session_type_annotation = "Optional[Session]"
    return_type_annotation = Generator[service_class, None, None]  # type: ignore[misc,assignment,valid-type]

    def provide_service_sync(*args: Any, **kwargs: Any) -> "Generator[SyncServiceT_co, None, None]":
        db_session = cast("Optional[Session]", args[0] if args else kwargs.get(session_dependency_key))
        with service_class.new(
            session=db_session,
            statement=statement,
            config=cast("Optional[SQLAlchemySyncConfig]", config),
            error_messages=error_messages,
            load=load,
            execution_options=execution_options,
            uniquify=uniquify,
            count_with_window_function=count_with_window_function,
        ) as service:
            yield service

    session_param = inspect.Parameter(
        name=session_dependency_key,
        kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
        default=Dependency(skip_validation=True),
        annotation=session_type_annotation,
    )

    provider_signature = inspect.Signature(
        parameters=[session_param],
        return_annotation=return_type_annotation,
    )
    provide_service_sync.__signature__ = provider_signature  # type: ignore[attr-defined]
    provide_service_sync.__annotations__ = {
        session_dependency_key: session_type_annotation,
        "return": return_type_annotation,
    }
    return provide_service_sync


def create_service_dependencies(
    service_class: type[Union["AsyncServiceT_co", "SyncServiceT_co"]],
    /,
    key: str,
    statement: "Optional[Select[tuple[ModelT]]]" = None,
    config: "Optional[Union[SQLAlchemyAsyncConfig, SQLAlchemySyncConfig]]" = None,
    error_messages: "Optional[Union[ErrorMessages, EmptyType]]" = Empty,
    load: "Optional[LoadSpec]" = None,
    execution_options: "Optional[dict[str, Any]]" = None,
    filters: "Optional[FilterConfig]" = None,
    uniquify: Optional[bool] = None,
    count_with_window_function: Optional[bool] = None,
    dep_defaults: "DependencyDefaults" = DEPENDENCY_DEFAULTS,
) -> dict[str, Provide]:
    """Create a dependency provider for the combined filter function.

    Args:
        key: The key to use for the dependency provider.
        service_class: The service class to create a dependency provider for.
        statement: The statement to use for the service.
        config: The configuration to use for the service.
        error_messages: The error messages to use for the service.
        load: The load spec to use for the service.
        execution_options: The execution options to use for the service.
        filters: The filter configuration to use for the service.
        uniquify: Whether to uniquify the service.
        count_with_window_function: Whether to count with a window function.
        dep_defaults: The dependency defaults to use for the service.

    Returns:
        A dictionary of dependency providers for the service.
    """

    if issubclass(service_class, SQLAlchemyAsyncRepositoryService) or service_class is SQLAlchemyAsyncRepositoryService:  # type: ignore[comparison-overlap]
        svc = create_service_provider(  # type: ignore[type-var,misc,unused-ignore]
            service_class,
            statement,
            cast("Optional[SQLAlchemyAsyncConfig]", config),
            error_messages,
            load,
            execution_options,
            uniquify,
            count_with_window_function,
        )
        deps = {key: Provide(svc)}
    else:
        svc = create_service_provider(  # type: ignore[assignment]
            service_class,
            statement,
            cast("Optional[SQLAlchemySyncConfig]", config),
            error_messages,
            load,
            execution_options,
            uniquify,
            count_with_window_function,
        )
        deps = {key: Provide(svc, sync_to_thread=False)}
    if filters:
        deps.update(create_filter_dependencies(filters, dep_defaults))
    return deps


def create_filter_dependencies(
    config: FilterConfig, dep_defaults: DependencyDefaults = DEPENDENCY_DEFAULTS
) -> dict[str, Provide]:
    """Create a dependency provider for the combined filter function.

    Args:
        config: FilterConfig instance with desired settings.
        dep_defaults: Dependency defaults to use for the filter dependencies

    Returns:
        A dependency provider function for the combined filter function.
    """
    cache_key = hash((_CACHE_NAMESPACE, make_hashable(config)))
    deps = cast("Optional[dict[str, Provide]]", dep_cache.get_dependencies(cache_key))
    if deps is not None:
        return deps
    deps = _create_statement_filters(config, dep_defaults)
    dep_cache.add_dependencies(cache_key, deps)
    return deps


def _create_statement_filters(  # noqa: C901
    config: FilterConfig, dep_defaults: DependencyDefaults = DEPENDENCY_DEFAULTS
) -> dict[str, Provide]:
    """Create filter dependencies based on configuration.

    Args:
        config (FilterConfig): Configuration dictionary specifying which filters to enable
        dep_defaults (DependencyDefaults): Dependency defaults to use for the filter dependencies

    Returns:
        dict[str, Provide]: Dictionary of filter provider functions
    """
    filters: dict[str, Provide] = {}

    if config.get("id_filter", False):

        def provide_id_filter(  # pyright: ignore[reportUnknownParameterType]
            ids: Optional[list[str]] = Parameter(query="ids", default=None, required=False),
        ) -> CollectionFilter:  # pyright: ignore[reportMissingTypeArgument]
            return CollectionFilter(field_name=config.get("id_field", "id"), values=ids)

        filters[dep_defaults.ID_FILTER_DEPENDENCY_KEY] = Provide(provide_id_filter, sync_to_thread=False)  # pyright: ignore[reportUnknownArgumentType]

    if config.get("created_at", False):

        def provide_created_filter(
            before: DTorNone = Parameter(query="createdBefore", default=None, required=False),
            after: DTorNone = Parameter(query="createdAfter", default=None, required=False),
        ) -> BeforeAfter:
            return BeforeAfter("created_at", before, after)

        filters[dep_defaults.CREATED_FILTER_DEPENDENCY_KEY] = Provide(provide_created_filter, sync_to_thread=False)

    if config.get("updated_at", False):

        def provide_updated_filter(
            before: DTorNone = Parameter(query="updatedBefore", default=None, required=False),
            after: DTorNone = Parameter(query="updatedAfter", default=None, required=False),
        ) -> BeforeAfter:
            return BeforeAfter("updated_at", before, after)

        filters[dep_defaults.UPDATED_FILTER_DEPENDENCY_KEY] = Provide(provide_updated_filter, sync_to_thread=False)

    if config.get("pagination_type") == "limit_offset":

        def provide_limit_offset_pagination(
            current_page: int = Parameter(ge=1, query="currentPage", default=1, required=False),
            page_size: int = Parameter(
                query="pageSize",
                ge=1,
                default=config.get("pagination_size", dep_defaults.DEFAULT_PAGINATION_SIZE),
                required=False,
            ),
        ) -> LimitOffset:
            return LimitOffset(page_size, page_size * (current_page - 1))

        filters[dep_defaults.LIMIT_OFFSET_FILTER_DEPENDENCY_KEY] = Provide(
            provide_limit_offset_pagination, sync_to_thread=False
        )

    if search_fields := config.get("search"):

        def provide_search_filter(
            search_string: StringOrNone = Parameter(
                title="Field to search",
                query="searchString",
                default=None,
                required=False,
            ),
            ignore_case: BooleanOrNone = Parameter(
                title="Search should be case sensitive",
                query="searchIgnoreCase",
                default=config.get("search_ignore_case", False),
                required=False,
            ),
        ) -> SearchFilter:
            # Handle both string and set input types for search fields
            field_names = set(search_fields.split(",")) if isinstance(search_fields, str) else set(search_fields)

            return SearchFilter(
                field_name=field_names,
                value=search_string,  # type: ignore[arg-type]
                ignore_case=ignore_case or False,
            )

        filters[dep_defaults.SEARCH_FILTER_DEPENDENCY_KEY] = Provide(provide_search_filter, sync_to_thread=False)

    if sort_field := config.get("sort_field"):

        def provide_order_by(
            field_name: StringOrNone = Parameter(
                title="Order by field",
                query="orderBy",
                default=sort_field,
                required=False,
            ),
            sort_order: SortOrderOrNone = Parameter(
                title="Field to search",
                query="sortOrder",
                default=config.get("sort_order", "desc"),
                required=False,
            ),
        ) -> OrderBy:
            return OrderBy(field_name=field_name, sort_order=sort_order)  # type: ignore[arg-type]

        filters[dep_defaults.ORDER_BY_FILTER_DEPENDENCY_KEY] = Provide(provide_order_by, sync_to_thread=False)

    # Add not_in filter providers
    if not_in_fields := config.get("not_in_fields"):
        # Get all field names, handling both strings and FieldNameType objects
        not_in_fields = {not_in_fields} if isinstance(not_in_fields, (str, FieldNameType)) else not_in_fields

        for field_def in not_in_fields:
            field_def = FieldNameType(name=field_def, type_hint=str) if isinstance(field_def, str) else field_def

            # Capture field_def by value to avoid Python closure late binding gotcha
            # Without default parameter, all closures would reference the loop variable's final value
            def create_not_in_filter_provider(  # pyright: ignore
                field_name: FieldNameType = field_def,  # type: ignore[assignment]
            ) -> Callable[..., Optional[NotInCollectionFilter[Any]]]:
                param_name = f"{field_name.name}_not_in"

                def provide_not_in_filter(  # pyright: ignore
                    **kwargs: Any,
                ) -> Optional[NotInCollectionFilter[field_name.type_hint]]:  # type: ignore
                    values = kwargs.get(param_name)
                    return (
                        NotInCollectionFilter[field_name.type_hint](field_name=field_name.name, values=values)  # type: ignore
                        if values
                        else None
                    )

                provide_not_in_filter.__name__ = f"provide_not_in_filter_{field_name.name}"
                provide_not_in_filter.__signature__ = inspect.Signature(  # type: ignore[attr-defined]
                    parameters=[
                        inspect.Parameter(
                            name=param_name,
                            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                            default=Parameter(
                                query=camelize(param_name),
                                default=None,
                                required=False,
                            ),
                            annotation=Optional[list[field_name.type_hint]],  # type: ignore
                        )
                    ],
                    return_annotation=Optional[NotInCollectionFilter[field_name.type_hint]],  # type: ignore
                )
                provide_not_in_filter.__annotations__ = {
                    param_name: Optional[list[field_name.type_hint]],  # type: ignore
                    "return": Optional[NotInCollectionFilter[field_name.type_hint]],  # type: ignore
                }
                return provide_not_in_filter  # pyright: ignore

            provider = create_not_in_filter_provider(field_def)  # pyright: ignore
            filters[f"{field_def.name}_not_in_filter"] = Provide(provider, sync_to_thread=False)  # pyright: ignore

    # Add in filter providers
    if in_fields := config.get("in_fields"):
        # Get all field names, handling both strings and FieldNameType objects
        in_fields = {in_fields} if isinstance(in_fields, (str, FieldNameType)) else in_fields

        for field_def in in_fields:
            field_def = FieldNameType(name=field_def, type_hint=str) if isinstance(field_def, str) else field_def

            # Capture field_def by value to avoid Python closure late binding gotcha
            # Without default parameter, all closures would reference the loop variable's final value
            def create_in_filter_provider(  # pyright: ignore
                field_name: FieldNameType = field_def,  # type: ignore[assignment]
            ) -> Callable[..., Optional[CollectionFilter[Any]]]:
                param_name = f"{field_name.name}_in"

                def provide_in_filter(  # pyright: ignore
                    **kwargs: Any,
                ) -> Optional[CollectionFilter[field_name.type_hint]]:  # type: ignore # pyright: ignore
                    values = kwargs.get(param_name)
                    return (
                        CollectionFilter[field_name.type_hint](field_name=field_name.name, values=values)  # type: ignore  # pyright: ignore
                        if values
                        else None
                    )

                provide_in_filter.__name__ = f"provide_in_filter_{field_name.name}"
                provide_in_filter.__signature__ = inspect.Signature(  # type: ignore[attr-defined]
                    parameters=[
                        inspect.Parameter(
                            name=param_name,
                            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                            default=Parameter(
                                query=camelize(param_name),
                                default=None,
                                required=False,
                            ),
                            annotation=Optional[list[field_name.type_hint]],  # type: ignore
                        )
                    ],
                    return_annotation=Optional[CollectionFilter[field_name.type_hint]],  # type: ignore
                )
                provide_in_filter.__annotations__ = {
                    param_name: Optional[list[field_name.type_hint]],  # type: ignore
                    "return": Optional[CollectionFilter[field_name.type_hint]],  # type: ignore
                }
                return provide_in_filter  # pyright: ignore

            provider = create_in_filter_provider(field_def)  # type: ignore
            filters[f"{field_def.name}_in_filter"] = Provide(provider, sync_to_thread=False)  # pyright: ignore

    if filters:
        filters[dep_defaults.FILTERS_DEPENDENCY_KEY] = Provide(
            _create_filter_aggregate_function(config), sync_to_thread=False
        )

    return filters


def _create_filter_aggregate_function(config: FilterConfig) -> Callable[..., list[FilterTypes]]:  # noqa: C901, PLR0915
    """Create a filter function based on the provided configuration.

    Args:
        config: The filter configuration.

    Returns:
        A function that returns a list of filters based on the configuration.
    """

    parameters: dict[str, inspect.Parameter] = {}
    annotations: dict[str, Any] = {}

    # Build parameters based on config
    if cls := config.get("id_filter"):
        parameters["id_filter"] = inspect.Parameter(
            name="id_filter",
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            default=Dependency(skip_validation=True),
            annotation=CollectionFilter[cls],  # type: ignore[valid-type]
        )
        annotations["id_filter"] = CollectionFilter[cls]  # type: ignore[valid-type]

    if config.get("created_at"):
        parameters["created_filter"] = inspect.Parameter(
            name="created_filter",
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            default=Dependency(skip_validation=True),
            annotation=BeforeAfter,
        )
        annotations["created_filter"] = BeforeAfter

    if config.get("updated_at"):
        parameters["updated_filter"] = inspect.Parameter(
            name="updated_filter",
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            default=Dependency(skip_validation=True),
            annotation=BeforeAfter,
        )
        annotations["updated_filter"] = BeforeAfter

    if config.get("search"):
        parameters["search_filter"] = inspect.Parameter(
            name="search_filter",
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            default=Dependency(skip_validation=True),
            annotation=SearchFilter,
        )
        annotations["search_filter"] = SearchFilter

    if config.get("pagination_type") == "limit_offset":
        parameters["limit_offset_filter"] = inspect.Parameter(
            name="limit_offset_filter",
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            default=Dependency(skip_validation=True),
            annotation=LimitOffset,
        )
        annotations["limit_offset_filter"] = LimitOffset

    if config.get("sort_field"):
        parameters["order_by_filter"] = inspect.Parameter(
            name="order_by_filter",
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            default=Dependency(skip_validation=True),
            annotation=OrderBy,
        )
        annotations["order_by_filter"] = OrderBy

    # Add parameters for not_in filters
    if not_in_fields := config.get("not_in_fields"):
        for field_def in not_in_fields:
            field_def = FieldNameType(name=field_def, type_hint=str) if isinstance(field_def, str) else field_def
            parameters[f"{field_def.name}_not_in_filter"] = inspect.Parameter(
                name=f"{field_def.name}_not_in_filter",
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=Dependency(skip_validation=True),
                annotation=NotInCollectionFilter[field_def.type_hint],  # type: ignore
            )
            annotations[f"{field_def.name}_not_in_filter"] = NotInCollectionFilter[field_def.type_hint]  # type: ignore

    # Add parameters for in filters
    if in_fields := config.get("in_fields"):
        for field_def in in_fields:
            field_def = FieldNameType(name=field_def, type_hint=str) if isinstance(field_def, str) else field_def
            parameters[f"{field_def.name}_in_filter"] = inspect.Parameter(
                name=f"{field_def.name}_in_filter",
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=Dependency(skip_validation=True),
                annotation=CollectionFilter[field_def.type_hint],  # type: ignore
            )
            annotations[f"{field_def.name}_in_filter"] = CollectionFilter[field_def.type_hint]  # type: ignore

    def provide_filters(**kwargs: FilterTypes) -> list[FilterTypes]:
        """Provide filter dependencies based on configuration.

        Args:
            **kwargs: Filter parameters dynamically provided based on configuration.

        Returns:
            list[FilterTypes]: List of configured filters.
        """
        filters: list[FilterTypes] = []
        if id_filter := kwargs.get("id_filter"):
            filters.append(id_filter)
        if created_filter := kwargs.get("created_filter"):
            filters.append(created_filter)
        if limit_offset := kwargs.get("limit_offset_filter"):
            filters.append(limit_offset)
        if updated_filter := kwargs.get("updated_filter"):
            filters.append(updated_filter)
        if (
            (search_filter := cast("Optional[SearchFilter]", kwargs.get("search_filter")))
            and search_filter is not None  # pyright: ignore[reportUnnecessaryComparison]
            and search_filter.field_name is not None  # pyright: ignore[reportUnnecessaryComparison]
            and search_filter.value is not None  # pyright: ignore[reportUnnecessaryComparison]
        ):
            filters.append(search_filter)
        if (
            (order_by := cast("Optional[OrderBy]", kwargs.get("order_by_filter")))
            and order_by is not None  # pyright: ignore[reportUnnecessaryComparison]
            and order_by.field_name is not None  # pyright: ignore[reportUnnecessaryComparison]
        ):
            filters.append(order_by)

        # Add not_in filters
        if not_in_fields := config.get("not_in_fields"):
            # Get all field names, handling both strings and FieldNameType objects
            not_in_fields = {not_in_fields} if isinstance(not_in_fields, (str, FieldNameType)) else not_in_fields
            for field_def in not_in_fields:
                field_def = FieldNameType(name=field_def, type_hint=str) if isinstance(field_def, str) else field_def
                filter_ = kwargs.get(f"{field_def.name}_not_in_filter")
                if filter_ is not None:
                    filters.append(filter_)

        # Add in filters
        if in_fields := config.get("in_fields"):
            # Get all field names, handling both strings and FieldNameType objects
            in_fields = {in_fields} if isinstance(in_fields, (str, FieldNameType)) else in_fields
            for field_def in in_fields:
                field_def = FieldNameType(name=field_def, type_hint=str) if isinstance(field_def, str) else field_def
                filter_ = kwargs.get(f"{field_def.name}_in_filter")
                if filter_ is not None:
                    filters.append(filter_)
        return filters

    # Set both signature and annotations
    provide_filters.__signature__ = inspect.Signature(  # type: ignore
        parameters=list(parameters.values()),
        return_annotation=list[FilterTypes],
    )
    provide_filters.__annotations__ = annotations
    provide_filters.__annotations__["return"] = list[FilterTypes]

    return provide_filters


# ============================================================================
# provide_async_services — out-of-DI service composition (CLI/listeners/jobs/guards)
# ============================================================================
#
# 10 overloads required: PEP 646 has no type-level map for
# Callable[..., AsyncGenerator[T, None]]; see python/typing#1361.
# Empirically verified against mypy 1.20.2 and pyright 1.1.409 (2026-04-26).
# For unbounded arity with full per-position typing, use
# advanced_alchemy.service.SQLAlchemyAsyncServiceComposition builder.

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
    p1: "SQLAlchemyAsyncServiceCompositionInput[T1]",
    /,
    *,
    config: "SQLAlchemyAsyncConfig",
    session: "Optional[AsyncSession]" = ...,
    connection: "Optional[ASGIConnection[Any, Any, Any, Any]]" = ...,
) -> "AbstractAsyncContextManager[tuple[T1]]": ...


@overload
def provide_async_services(
    p1: "SQLAlchemyAsyncServiceCompositionInput[T1]",
    p2: "SQLAlchemyAsyncServiceCompositionInput[T2]",
    /,
    *,
    config: "SQLAlchemyAsyncConfig",
    session: "Optional[AsyncSession]" = ...,
    connection: "Optional[ASGIConnection[Any, Any, Any, Any]]" = ...,
) -> "AbstractAsyncContextManager[tuple[T1, T2]]": ...


@overload
def provide_async_services(
    p1: "SQLAlchemyAsyncServiceCompositionInput[T1]",
    p2: "SQLAlchemyAsyncServiceCompositionInput[T2]",
    p3: "SQLAlchemyAsyncServiceCompositionInput[T3]",
    /,
    *,
    config: "SQLAlchemyAsyncConfig",
    session: "Optional[AsyncSession]" = ...,
    connection: "Optional[ASGIConnection[Any, Any, Any, Any]]" = ...,
) -> "AbstractAsyncContextManager[tuple[T1, T2, T3]]": ...


@overload
def provide_async_services(
    p1: "SQLAlchemyAsyncServiceCompositionInput[T1]",
    p2: "SQLAlchemyAsyncServiceCompositionInput[T2]",
    p3: "SQLAlchemyAsyncServiceCompositionInput[T3]",
    p4: "SQLAlchemyAsyncServiceCompositionInput[T4]",
    /,
    *,
    config: "SQLAlchemyAsyncConfig",
    session: "Optional[AsyncSession]" = ...,
    connection: "Optional[ASGIConnection[Any, Any, Any, Any]]" = ...,
) -> "AbstractAsyncContextManager[tuple[T1, T2, T3, T4]]": ...


@overload
def provide_async_services(
    p1: "SQLAlchemyAsyncServiceCompositionInput[T1]",
    p2: "SQLAlchemyAsyncServiceCompositionInput[T2]",
    p3: "SQLAlchemyAsyncServiceCompositionInput[T3]",
    p4: "SQLAlchemyAsyncServiceCompositionInput[T4]",
    p5: "SQLAlchemyAsyncServiceCompositionInput[T5]",
    /,
    *,
    config: "SQLAlchemyAsyncConfig",
    session: "Optional[AsyncSession]" = ...,
    connection: "Optional[ASGIConnection[Any, Any, Any, Any]]" = ...,
) -> "AbstractAsyncContextManager[tuple[T1, T2, T3, T4, T5]]": ...


@overload
def provide_async_services(
    p1: "SQLAlchemyAsyncServiceCompositionInput[T1]",
    p2: "SQLAlchemyAsyncServiceCompositionInput[T2]",
    p3: "SQLAlchemyAsyncServiceCompositionInput[T3]",
    p4: "SQLAlchemyAsyncServiceCompositionInput[T4]",
    p5: "SQLAlchemyAsyncServiceCompositionInput[T5]",
    p6: "SQLAlchemyAsyncServiceCompositionInput[T6]",
    /,
    *,
    config: "SQLAlchemyAsyncConfig",
    session: "Optional[AsyncSession]" = ...,
    connection: "Optional[ASGIConnection[Any, Any, Any, Any]]" = ...,
) -> "AbstractAsyncContextManager[tuple[T1, T2, T3, T4, T5, T6]]": ...


@overload
def provide_async_services(
    p1: "SQLAlchemyAsyncServiceCompositionInput[T1]",
    p2: "SQLAlchemyAsyncServiceCompositionInput[T2]",
    p3: "SQLAlchemyAsyncServiceCompositionInput[T3]",
    p4: "SQLAlchemyAsyncServiceCompositionInput[T4]",
    p5: "SQLAlchemyAsyncServiceCompositionInput[T5]",
    p6: "SQLAlchemyAsyncServiceCompositionInput[T6]",
    p7: "SQLAlchemyAsyncServiceCompositionInput[T7]",
    /,
    *,
    config: "SQLAlchemyAsyncConfig",
    session: "Optional[AsyncSession]" = ...,
    connection: "Optional[ASGIConnection[Any, Any, Any, Any]]" = ...,
) -> "AbstractAsyncContextManager[tuple[T1, T2, T3, T4, T5, T6, T7]]": ...


@overload
def provide_async_services(
    p1: "SQLAlchemyAsyncServiceCompositionInput[T1]",
    p2: "SQLAlchemyAsyncServiceCompositionInput[T2]",
    p3: "SQLAlchemyAsyncServiceCompositionInput[T3]",
    p4: "SQLAlchemyAsyncServiceCompositionInput[T4]",
    p5: "SQLAlchemyAsyncServiceCompositionInput[T5]",
    p6: "SQLAlchemyAsyncServiceCompositionInput[T6]",
    p7: "SQLAlchemyAsyncServiceCompositionInput[T7]",
    p8: "SQLAlchemyAsyncServiceCompositionInput[T8]",
    /,
    *,
    config: "SQLAlchemyAsyncConfig",
    session: "Optional[AsyncSession]" = ...,
    connection: "Optional[ASGIConnection[Any, Any, Any, Any]]" = ...,
) -> "AbstractAsyncContextManager[tuple[T1, T2, T3, T4, T5, T6, T7, T8]]": ...


@overload
def provide_async_services(
    p1: "SQLAlchemyAsyncServiceCompositionInput[T1]",
    p2: "SQLAlchemyAsyncServiceCompositionInput[T2]",
    p3: "SQLAlchemyAsyncServiceCompositionInput[T3]",
    p4: "SQLAlchemyAsyncServiceCompositionInput[T4]",
    p5: "SQLAlchemyAsyncServiceCompositionInput[T5]",
    p6: "SQLAlchemyAsyncServiceCompositionInput[T6]",
    p7: "SQLAlchemyAsyncServiceCompositionInput[T7]",
    p8: "SQLAlchemyAsyncServiceCompositionInput[T8]",
    p9: "SQLAlchemyAsyncServiceCompositionInput[T9]",
    /,
    *,
    config: "SQLAlchemyAsyncConfig",
    session: "Optional[AsyncSession]" = ...,
    connection: "Optional[ASGIConnection[Any, Any, Any, Any]]" = ...,
) -> "AbstractAsyncContextManager[tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9]]": ...


@overload
def provide_async_services(
    p1: "SQLAlchemyAsyncServiceCompositionInput[T1]",
    p2: "SQLAlchemyAsyncServiceCompositionInput[T2]",
    p3: "SQLAlchemyAsyncServiceCompositionInput[T3]",
    p4: "SQLAlchemyAsyncServiceCompositionInput[T4]",
    p5: "SQLAlchemyAsyncServiceCompositionInput[T5]",
    p6: "SQLAlchemyAsyncServiceCompositionInput[T6]",
    p7: "SQLAlchemyAsyncServiceCompositionInput[T7]",
    p8: "SQLAlchemyAsyncServiceCompositionInput[T8]",
    p9: "SQLAlchemyAsyncServiceCompositionInput[T9]",
    p10: "SQLAlchemyAsyncServiceCompositionInput[T10]",
    /,
    *,
    config: "SQLAlchemyAsyncConfig",
    session: "Optional[AsyncSession]" = ...,
    connection: "Optional[ASGIConnection[Any, Any, Any, Any]]" = ...,
) -> "AbstractAsyncContextManager[tuple[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10]]": ...


@overload
def provide_async_services(
    *providers: "SQLAlchemyAsyncServiceCompositionInput[Any]",
    config: "SQLAlchemyAsyncConfig",
    session: "Optional[AsyncSession]" = ...,
    connection: "Optional[ASGIConnection[Any, Any, Any, Any]]" = ...,
) -> "AbstractAsyncContextManager[tuple[Any, ...]]": ...


@asynccontextmanager
async def provide_async_services(
    *providers: "SQLAlchemyAsyncServiceCompositionInput[Any]",
    config: "SQLAlchemyAsyncConfig",
    session: "Optional[AsyncSession]" = None,
    connection: "Optional[ASGIConnection[Any, Any, Any, Any]]" = None,
) -> "AsyncGenerator[tuple[Any, ...], None]":
    r"""Compose multiple services on a shared session — Litestar-aware.

    Three operating modes (mutually exclusive):

    1. **Explicit session** — caller passes ``session=`` and owns the session
       lifecycle (commit/rollback/close).
    2. **Connection-scoped** — caller passes ``connection=`` (Litestar
       ``ASGIConnection`\"); session is resolved via
       ``config.provide_session(connection.app.state, connection.scope)``,
       reusing the request-scoped session.
    3. **Standalone** — caller passes neither; a fresh session is opened via
       ``config.get_session()`` and closed on exit.

    Args:
        *providers: 1-10 service-provider callables or classes (typed) or any number
            (typed as ``Any`` via the fallback overload).
        config: SQLAlchemy async config — required in all modes for session resolution.
        session: Optional pre-existing session (mode 1).
        connection: Optional Litestar ASGI connection (mode 2).

    Raises:
        ValueError: If both ``session`` and ``connection`` are provided.
        ValueError: If no providers are passed.

    Yields:
        Tuple of N services in the order their providers were passed.

    Example:
        .. code-block:: python

            # CLI / background job (standalone mode):
            async with provide_async_services(
                provide_users_service,
                provide_roles_service,
                config=alchemy,
            ) as (users, roles):
                await users.create(...)
                await roles.create(...)

            # Litestar guard (connection-scoped):
            async with provide_async_services(
                provide_users_service,
                config=alchemy,
                connection=connection,
            ) as (users,):
                return await users.get_one_or_none(email=token.sub)
    """
    if session is not None and connection is not None:
        msg = "Cannot provide both 'session' and 'connection' — choose one"
        raise ValueError(msg)
    if not providers:
        msg = "At least one service provider or class is required"
        raise ValueError(msg)

    composer: Any = SQLAlchemyAsyncServiceComposition.starting_with(providers[0])
    for p in providers[1:]:
        composer = composer.add(p)

    if session is not None:
        async with composer.open(session=session) as services:
            yield services
    elif connection is not None:
        db_session = config.provide_session(connection.app.state, connection.scope)
        async with composer.open(session=db_session) as services:
            yield services
    else:
        async with config.get_session() as db_session, composer.open(session=db_session) as services:
            yield services
