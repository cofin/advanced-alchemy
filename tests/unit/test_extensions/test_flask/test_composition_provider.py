import pytest
from flask import Flask, g
from sqlalchemy.orm import Session

from advanced_alchemy.base import BigIntBase
from advanced_alchemy.extensions.flask import AdvancedAlchemy, SQLAlchemySyncConfig
from advanced_alchemy.extensions.flask.providers import provide_sync_services
from advanced_alchemy.repository import SQLAlchemySyncRepository
from advanced_alchemy.service import SQLAlchemySyncRepositoryService


class FlaskUser(BigIntBase):
    pass


class FlaskUserService(SQLAlchemySyncRepositoryService[FlaskUser]):
    class Repo(SQLAlchemySyncRepository[FlaskUser]):
        model_type = FlaskUser

    repository_type = Repo


class FlaskTask(BigIntBase):
    pass


class FlaskTaskService(SQLAlchemySyncRepositoryService[FlaskTask]):
    class Repo(SQLAlchemySyncRepository[FlaskTask]):
        model_type = FlaskTask

    repository_type = Repo


@pytest.fixture
def config() -> SQLAlchemySyncConfig:
    return SQLAlchemySyncConfig(connection_string="sqlite:///:memory:")


@pytest.fixture
def extension(config: SQLAlchemySyncConfig) -> AdvancedAlchemy:
    return AdvancedAlchemy(config=config)


def test_provide_sync_services_explicit_session(config: SQLAlchemySyncConfig) -> None:
    with config.get_session() as session:
        with provide_sync_services(FlaskUserService, session=session, config=config) as (flask_user_service,):
            assert isinstance(flask_user_service, FlaskUserService)
            assert flask_user_service.repository.session is session


def test_provide_sync_services_standalone(config: SQLAlchemySyncConfig) -> None:
    with provide_sync_services(FlaskUserService, config=config) as (flask_user_service,):
        assert isinstance(flask_user_service, FlaskUserService)
        assert isinstance(flask_user_service.repository.session, Session)


def test_provide_sync_services_app_scoped(config: SQLAlchemySyncConfig) -> None:
    app = Flask(__name__)
    with app.app_context():
        with config.get_session() as session:
            bind_key = config.bind_key or "default"
            setattr(g, f"advanced_alchemy_session_{bind_key}", session)
            with provide_sync_services(FlaskUserService, FlaskTaskService, config=config) as (
                flask_user_service,
                flask_task_service,
            ):
                assert isinstance(flask_user_service, FlaskUserService)
                assert isinstance(flask_task_service, FlaskTaskService)
                assert flask_user_service.repository.session is session
                assert flask_task_service.repository.session is session


def test_provide_sync_services_errors(config: SQLAlchemySyncConfig) -> None:
    # No inputs
    with pytest.raises(ValueError, match="At least one service provider or class is required"):
        with provide_sync_services(config=config):  # type: ignore
            pass
