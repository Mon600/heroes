import logging
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_db_url():
    return (f'postgresql+asyncpg://'
            f'{os.getenv("DB_USER")}:'
            f'{os.getenv("DB_PASSWORD")}@'
            f'{os.getenv("DB_HOST")}:'
            f'{os.getenv("DB_PORT")}/'
            f'{os.getenv("DB_NAME")}')


def get_engine():
    db_url = get_db_url()
    engine = create_async_engine(url=db_url)
    return engine

async_session = async_sessionmaker(get_engine(), expire_on_commit=False)

def get_api_access():
    return os.getenv("API_ACCESS")


class Base(DeclarativeBase):
    pass