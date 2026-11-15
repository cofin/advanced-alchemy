"""Service groups share SQL and mock grid-filter behavior."""

from __future__ import annotations

from collections.abc import Sequence

import pytest
from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

from advanced_alchemy.filters import LimitOffset, StatementFilter
from advanced_alchemy.repository.memory import SQLAlchemyAsyncMockRepository, SQLAlchemySyncMockRepository
from advanced_alchemy.service import ServiceGroup, SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService
from advanced_alchemy.utils.dependencies import (
    build_grid_filters_for_group,
    build_order_by_filters,
    resolve_grid_filter_fields,
)

pytestmark = pytest.mark.unit


class GridBase(DeclarativeBase):
    pass


class GridAuthor(GridBase):
    __tablename__ = "group_grid_author"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


class GridArticle(GridBase):
    __tablename__ = "group_grid_article"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey(GridAuthor.id))
    author: Mapped[GridAuthor] = relationship(lazy="joined")


def grid_filters() -> Sequence[StatementFilter]:
    specs = resolve_grid_filter_fields({"author.name": {"eq"}}, GridArticle)
    author_filter = build_grid_filters_for_group(specs, {specs[0].param_name: "Ada"}, rel_path=("author",))
    assert isinstance(author_filter, StatementFilter)
    return [
        author_filter,
        *build_order_by_filters(["author.name", "-title"], None, allowed_fields={"author.name", "title"}),
        LimitOffset(limit=1, offset=1),
    ]


def articles(authors: Sequence[GridAuthor]) -> list[GridArticle]:
    return [
        GridArticle(id=1, title="Alpha", author=authors[0]),
        GridArticle(id=2, title="Zulu", author=authors[0]),
        GridArticle(id=3, title="Other", author=authors[1]),
        GridArticle(id=4, title="Middle", author=authors[0]),
    ]


@pytest.mark.parametrize("use_mock", [False, True])
def test_sync_service_group_grid_filter_parity(use_mock: bool) -> None:
    """Related grid filtering preserves ordering and totals in a shared group."""

    class AuthorService(SQLAlchemySyncRepositoryService[GridAuthor]):
        pass

    class ArticleService(SQLAlchemySyncRepositoryService[GridArticle]):
        pass

    class AuthorRepo(SQLAlchemySyncMockRepository[GridAuthor]):
        pass

    class ArticleRepo(SQLAlchemySyncMockRepository[GridArticle]):
        pass

    if use_mock:
        AuthorRepo.__database_clear__()
        ArticleRepo.__database_clear__()
        AuthorService.repository_type = AuthorRepo
        ArticleService.repository_type = ArticleRepo

    class Group(ServiceGroup):
        authors: AuthorService
        articles: ArticleService

    engine = create_engine("sqlite://")
    try:
        GridBase.metadata.create_all(engine)
        with Session(engine) as session, Group.new(session=session) as group:
            assert group.authors.repository.session is group.articles.repository.session is session
            authors = group.authors.create_many([GridAuthor(id=1, name="Ada"), GridAuthor(id=2, name="Bob")])
            group.articles.create_many(articles(authors))
            items, total = group.articles.get_many_and_count(*grid_filters())
            assert ([item.id for item in items], total) == ([4], 3)
            assert group.authors.count() == 2
    finally:
        engine.dispose()
        if use_mock:
            AuthorRepo.__database_clear__()
            ArticleRepo.__database_clear__()


@pytest.mark.parametrize("use_mock", [False, True])
async def test_async_service_group_grid_filter_parity(use_mock: bool) -> None:
    """Async groups preserve the same related grid results as SQL and sync groups."""

    class AuthorService(SQLAlchemyAsyncRepositoryService[GridAuthor]):
        pass

    class ArticleService(SQLAlchemyAsyncRepositoryService[GridArticle]):
        pass

    class AuthorRepo(SQLAlchemyAsyncMockRepository[GridAuthor]):
        pass

    class ArticleRepo(SQLAlchemyAsyncMockRepository[GridArticle]):
        pass

    if use_mock:
        AuthorRepo.__database_clear__()
        ArticleRepo.__database_clear__()
        AuthorService.repository_type = AuthorRepo
        ArticleService.repository_type = ArticleRepo

    class Group(ServiceGroup):
        authors: AuthorService
        articles: ArticleService

    engine = create_async_engine("sqlite+aiosqlite://")
    try:
        async with engine.begin() as connection:
            await connection.run_sync(GridBase.metadata.create_all)
        async with AsyncSession(engine) as session, Group.new(session=session) as group:
            assert group.authors.repository.session is group.articles.repository.session is session
            authors = await group.authors.create_many([GridAuthor(id=1, name="Ada"), GridAuthor(id=2, name="Bob")])
            await group.articles.create_many(articles(authors))
            items, total = await group.articles.get_many_and_count(*grid_filters())
            assert ([item.id for item in items], total) == ([4], 3)
            assert await group.authors.count() == 2
    finally:
        await engine.dispose()
        if use_mock:
            AuthorRepo.__database_clear__()
            ArticleRepo.__database_clear__()
