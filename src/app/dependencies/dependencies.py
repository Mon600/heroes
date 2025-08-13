from typing import AsyncGenerator, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import async_session
from src.app.db.repository.repository import Repository
from src.app.services.service import Service


async def get_session() -> AsyncGenerator:
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_repository(session: SessionDep) -> Repository:
    return Repository(session)

RepositoryDep = Annotated[Repository, Depends(get_repository)]


async def get_service(repository: RepositoryDep) -> Service:
    return Service(repository)

ServiceDep = Annotated[Service, Depends(get_service)]