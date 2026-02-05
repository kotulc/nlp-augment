import json
import logging

from sqlmodel import create_engine, Session, SQLModel

from app.crud.tables import Metric, Summary, Tag
from app.settings import get_settings


# Define database engine
settings = get_settings().database
engine = create_engine(settings.url, connect_args=settings.connect_args)


def init_database():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def store_result(operation: str, result: dict) -> None:
    logger = logging.getLogger(__name__)
    with next(get_session()) as session:
        match operation:
            case "metrics":
                db_operation = Metric(**result)
            case "summary":
                db_operation = Summary(**result)
            case "tags":
                db_operation = Tag(**result)
            case _:
                logger.warning("Unknown operation type: %s", operation)
                return
        session.add(db_operation)
        session.commit()
