from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker, Session
from os import getenv

DATABASE_URL = URL.create(
    drivername=f'{getenv("DB_CONNECTION")}+{getenv("DB_DRIVER")}',
    username=getenv("DB_USERNAME"),
    password=getenv("DB_PASSWORD"),
    host=getenv("DB_HOST"),
    port=int(getenv("DB_PORT")),
    database=getenv("DB_NAME")
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()