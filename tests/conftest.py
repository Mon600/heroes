import asyncio
import logging
import os
from typing import AsyncGenerator, Optional
from unittest.mock import AsyncMock

import pytest_asyncio
from dotenv import load_dotenv
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from main import app
from src.app.db.repository.repository import Repository
from src.app.dependencies.dependencies import get_service
from src.app.pydantic_models.schemas import FiltersSchema, HeroResponse
from src.app.services.service import Service
from src.config import Base

load_dotenv()


def get_test_db_url():
    return (
        f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/test_heroes"
    )


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_database():
    temp_url = "postgresql+asyncpg://postgres:1@localhost:5432/postgres"
    temp_engine = create_async_engine(temp_url, isolation_level="AUTOCOMMIT", poolclass=NullPool)

    async with temp_engine.begin() as conn:
        try:
            await conn.execute(text("DROP DATABASE IF EXISTS test_heroes WITH (FORCE)"))
        except Exception as e:
            print(f"Предупреждение: не удалось удалить базу: {e}")

        try:
            await conn.execute(text("CREATE DATABASE test_heroes"))
        except Exception as e:
            print(f"Ошибка: не удалось создать базу: {e}")
            raise

    await temp_engine.dispose()

    yield

    temp_engine = create_async_engine(temp_url, isolation_level="AUTOCOMMIT", poolclass=NullPool)
    async with temp_engine.begin() as conn:
        try:
            await conn.execute(text("DROP DATABASE IF EXISTS test_heroes WITH (FORCE)"))
        except Exception as e:
            print(f"Ошибка при очистке: {e}")
    await temp_engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def engine(create_test_database):
    test_url = get_test_db_url()
    eng = create_async_engine(test_url, poolclass=NullPool)

    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield eng

    await eng.dispose()


@pytest_asyncio.fixture(scope="session")
async def sessionmaker(engine: engine):
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def session(sessionmaker) -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as conn:
        try:
            yield conn
        except Exception as e:
            await conn.rollback()
            raise e
        finally:
            await conn.close()


@pytest_asyncio.fixture(scope="function")
def repository(session: AsyncSession) -> Repository:
    return Repository(session)


@pytest_asyncio.fixture(scope="function")
def service(
        repository: Repository,
) -> Service:
    service = Service(repository)
    service.logger = logging.getLogger("test")
    return service

@pytest_asyncio.fixture(scope="function")
def mock_service() -> AsyncMock:
    mock = AsyncMock(spec=Service)

    async def save_hero_side_effect(name: str):

        if name.lower() == "superman":
            return HeroResponse(
                name="Superman",
                intelligence=94,
                strength=100,
                speed=100,
                durability=100,
                power=100,
                combat=85
            )
        elif name.lower() == "batman":
            return HeroResponse(
                name="Batman",
                intelligence=100,
                strength=26,
                speed=27,
                durability=50,
                power=47,
                combat=100
            )
        else:
            raise ValueError('No result')

    async def get_heroes_side_effect(filters: FiltersSchema):
        all_heroes = [
            {
                "name": "Batman",
                "intelligence": 100,
                "strength": 26,
                "speed": 27,
                "durability": 50,
                "power": 47,
                "combat": 100
            },
            {
                "name": "Superman",
                "intelligence": 94,
                "strength": 100,
                "speed": 100,
                "durability": 100,
                "power": 100,
                "combat": 85
            },
            {
                "name": "Flash",
                "intelligence": 80,
                "strength": 70,
                "speed": 100,
                "durability": 75,
                "power": 90,
                "combat": 60
            },
            {
                "name": "Iron Man",
                "intelligence": 100,
                "strength": 85,
                "speed": 80,
                "durability": 85,
                "power": 90,
                "combat": 70
            }
        ]

        def matches_filter(value: int, filter_value: Optional[int], operator: str) -> bool:
            if filter_value is None:
                return True
            if operator == 'eq':
                return value == filter_value
            elif operator == 'ge':
                return value >= filter_value
            elif operator == 'le':
                return value <= filter_value
            return False

        filtered_heroes = []
        for hero in all_heroes:
            if filters.name and filters.name.lower() != hero["name"].lower():
                continue

            if not matches_filter(hero["intelligence"], filters.intelligence, filters.intelligence_operator):
                continue
            if not matches_filter(hero["strength"], filters.strength, filters.strength_operator):
                continue
            if not matches_filter(hero["speed"], filters.speed, filters.speed_operator):
                continue
            if not matches_filter(hero["durability"], filters.durability, filters.durability_operator):
                continue
            if not matches_filter(hero["power"], filters.power, filters.power_operator):
                continue
            if not matches_filter(hero["combat"], filters.combat, filters.combat_operator):
                continue

            filtered_heroes.append(hero)

        return filtered_heroes

    mock.save_hero.side_effect = save_hero_side_effect
    mock.get_heroes.side_effect = get_heroes_side_effect

    return mock


@pytest_asyncio.fixture(scope="function", autouse=True)
async def configured_app() -> FastAPI:
    return app


@pytest_asyncio.fixture(scope="function")
def integration_override_dependencies(configured_app: FastAPI, service):
    configured_app.dependency_overrides[get_service] = lambda: service
    yield
    configured_app.dependency_overrides = {}

@pytest_asyncio.fixture(scope="function")
def unit_test_override(configured_app: FastAPI, mock_service: AsyncMock):
    configured_app.dependency_overrides[get_service] = lambda: mock_service
    yield
    configured_app.dependency_overrides.clear()



@pytest_asyncio.fixture(scope="function")
async def async_client(configured_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    BASE_URL = "http://test"
    async with AsyncClient(
            transport=ASGITransport(app=configured_app),
            base_url=BASE_URL
    ) as client:
        yield client
