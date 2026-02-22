from sqlmodel import create_engine, Session, SQLModel

from app.settings import get_settings


# Define database engine
settings = get_settings().database
engine = create_engine(settings.url, connect_args=settings.connect_args)


def init_database():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
