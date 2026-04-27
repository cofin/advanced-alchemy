from contextlib import AbstractAsyncContextManager
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest
from typing_extensions import assert_type

from advanced_alchemy.base import BigIntBase
from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import (
    SQLAlchemyAsyncRepositoryService,
    provide_async_services,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def mock_async_session() -> MagicMock:
    return MagicMock()


class Model(BigIntBase):
    __tablename__ = "test_model"


class S1(SQLAlchemyAsyncRepositoryService[Model]):
    class Repo(SQLAlchemyAsyncRepository[Model]):
        model_type = Model

    repository_type = Repo


class S2(SQLAlchemyAsyncRepositoryService[Model]):
    class Repo(SQLAlchemyAsyncRepository[Model]):
        model_type = Model

    repository_type = Repo


class S3(SQLAlchemyAsyncRepositoryService[Model]):
    class Repo(SQLAlchemyAsyncRepository[Model]):
        model_type = Model

    repository_type = Repo


class S4(SQLAlchemyAsyncRepositoryService[Model]):
    class Repo(SQLAlchemyAsyncRepository[Model]):
        model_type = Model

    repository_type = Repo


class S5(SQLAlchemyAsyncRepositoryService[Model]):
    class Repo(SQLAlchemyAsyncRepository[Model]):
        model_type = Model

    repository_type = Repo


class S6(SQLAlchemyAsyncRepositoryService[Model]):
    class Repo(SQLAlchemyAsyncRepository[Model]):
        model_type = Model

    repository_type = Repo


class S7(SQLAlchemyAsyncRepositoryService[Model]):
    class Repo(SQLAlchemyAsyncRepository[Model]):
        model_type = Model

    repository_type = Repo


class S8(SQLAlchemyAsyncRepositoryService[Model]):
    class Repo(SQLAlchemyAsyncRepository[Model]):
        model_type = Model

    repository_type = Repo


class S9(SQLAlchemyAsyncRepositoryService[Model]):
    class Repo(SQLAlchemyAsyncRepository[Model]):
        model_type = Model

    repository_type = Repo


class S10(SQLAlchemyAsyncRepositoryService[Model]):
    class Repo(SQLAlchemyAsyncRepository[Model]):
        model_type = Model

    repository_type = Repo


async def test_provide_services_typing(mock_async_session: "AsyncSession") -> None:
    # 2-tuple overload
    res2 = provide_async_services(S1, S2, session=mock_async_session)
    assert_type(res2, AbstractAsyncContextManager[tuple[S1, S2]])

    # 10-tuple overload
    async with provide_async_services(S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, session=mock_async_session) as services:
        assert_type(services, tuple[S1, S2, S3, S4, S5, S6, S7, S8, S9, S10])
