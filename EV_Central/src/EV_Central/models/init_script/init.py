from sqlalchemy import create_engine, URL
from os import getenv

from ..Base import Base

def get_connection_url() -> URL:
    return URL.create(
        drivername=f'{getenv('DB_CONNECTION')}+{getenv('DB_DRIVER')}',
        username=getenv('DB_USERNAME'),
        password=getenv('DB_PASSWORD'),
        host=getenv('DB_HOST'),
        port=int(getenv('DB_PORT')),
        database=getenv('DB_NAME')
    )

def delete_db() -> None:
    engine = create_engine(get_connection_url())
    Base.metadata.drop_all(bind=engine)


def init_db() -> None:
    engine = create_engine(get_connection_url())
    Base.metadata.create_all(bind=engine)


if __name__ == '__main__':
    pass